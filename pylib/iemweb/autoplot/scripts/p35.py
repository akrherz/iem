"""
This plot presents a histogram of the change
in some observed variable over a given number of hours.  The histogram is
constructed by computing the 99.9th percentile of the absolute value of the
change in the variable over the given number of hours.  This max value is
then used to create a histogram with bins of a given width.  The histogram
is then normalized by the number of years of data available.
"""

import calendar
import datetime

import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context
from sqlalchemy import text

PDICT = {
    "tmpf": "Air Temp (F)",
    "alti": "Altimeter (in)",
    "dwpf": "Dew Point Temp (F)",
    "feel": "Feels Like Temp (F)",
    "mslp": "Mean Sea Level Pressure (mb)",
    "relh": "Relative Humidity (%)",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "cache": 86400, "data": True}
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="DSM",
            label="Select Station:",
            network="IA_ASOS",
        ),
        dict(
            type="select",
            options=PDICT,
            default="tmpf",
            name="var",
            label="Select Variable",
        ),
        dict(type="int", name="hours", default=24, label="Hours:"),
        dict(
            type="float",
            name="interval",
            default=1,
            label="Histogram Binning Width (unit of variable)",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["zstation"]
    hours = ctx["hours"]
    interval = ctx["interval"]
    varname = ctx["var"]
    if interval > 10 or interval < 0.1:
        raise NoDataFound(
            "Invalid interval provided, positive number less than 10"
        )

    with get_sqlalchemy_conn("asos") as conn:
        obs = pd.read_sql(
            text(f"""
        WITH one as (
            select valid, {varname} as t from alldata where
            station = :station and {varname} is not null and report_type = 3
            ),
            two as (SELECT valid + :hours as v, t from one
            )

        SELECT extract(week from one.valid) as week, two.t - one.t as delta,
        valid
        from one JOIN two on (one.valid = two.v)
        """),
            conn,
            params={
                "station": station,
                "hours": datetime.timedelta(hours=hours),
            },
            parse_dates="valid",
        )
    if obs.empty:
        raise NoDataFound("No non-null data found")

    sts = datetime.datetime(2012, 1, 1)
    xticks = []
    for i in range(1, 13):
        ts = sts.replace(month=i)
        xticks.append(int(ts.strftime("%j")))

    # We want bins centered on zero
    p99 = obs["delta"].abs().quantile(0.999)
    bins = np.arange(0 - p99, p99, interval)

    hist, xedges, yedges = np.histogram2d(
        obs["week"].values, obs["delta"].values, [range(54), bins]
    )
    # create a dataframe from this 2d histogram
    x, y = np.meshgrid(xedges[:-1], yedges[:-1])
    resultdf = pd.DataFrame(
        {
            "week": np.ravel(x),
            "delta": np.ravel(y),
            "count": np.ravel(hist),
        }
    )
    years = obs["valid"].dt.year.nunique()
    hist = np.ma.array(hist / years)
    hist.mask = np.where(hist < (1.0 / years / 7.0 / 24.0), True, False)

    title = (
        f"{ctx['_sname']} ({obs['valid'].min():%Y}-"
        f"{obs['valid'].max():%Y}):: Histogram"
    )
    subtitle = (
        f"(bin={interval}) of {hours} Hour {PDICT[varname]} Change, "
        f"99.9th percentile: {p99:.1f}, n={len(obs.index)}, years={years}"
    )
    (fig, ax) = figure_axes(title=title, subtitle=subtitle, apctx=ctx)
    res = ax.pcolormesh((xedges - 1) * 7, yedges, hist.transpose())
    fig.colorbar(res, label="Hours per Week")
    ax.grid(True)
    ax.set_ylabel(f"{PDICT[varname]} Change")

    ax.set_xticks(xticks)
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(0, 366)

    ax.set_ylim(0 - p99, p99)

    return fig, resultdf
