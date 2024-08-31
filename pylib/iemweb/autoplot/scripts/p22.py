"""
This plot displays the frequency of a daily high
or low temperature being within a certain bounds of the long term NCEI
climatology for the location.
"""

import calendar

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context
from sqlalchemy import text

from iemweb.autoplot import ARG_STATION

PDICT = {"high": "High temperature", "low": "Low Temperature"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        ARG_STATION,
        dict(
            type="int",
            name="min",
            default="-5",
            label="Lower Bound (F) of Temperature Range",
        ),
        dict(
            type="int",
            name="max",
            default="5",
            label="Upper Bound (F) of Temperature Range",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    minv = ctx["min"]
    maxv = ctx["max"]
    if minv > maxv:
        minv, maxv = maxv, minv
    station = ctx["station"]
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            text("""
        WITH climate as (
            SELECT to_char(valid, 'mmdd') as sday, high, low from
            ncei_climate91 where station = :ncei
        )
        SELECT extract(doy from day) as doy, count(*),
        SUM(case when a.high >= (c.high + :minv) and a.high < (c.high + :maxv)
                then 1 else 0 end) as high_count,
        SUM(case when a.low >= (c.low + :minv) and a.low < (c.low + :maxv)
                then 1 else 0 end) as low_count
        FROM alldata a JOIN climate c on (a.sday = c.sday)
        WHERE a.sday != '0229' and station = :station
        GROUP by doy ORDER by doy ASC
        """),
            conn,
            params={
                "ncei": ctx["_nt"].sts[station]["ncei91"],
                "minv": minv,
                "maxv": maxv,
                "station": station,
            },
            index_col="doy",
        )
    if df.empty:
        raise NoDataFound("No Data Found.")

    df["high_freq"] = df["high_count"] / df["count"] * 100.0
    df["low_freq"] = df["low_count"] / df["count"] * 100.0
    hvals = df["high_freq"].rolling(7, min_periods=1).mean().values
    lvals = df["low_freq"].rolling(7, min_periods=1).mean().values
    title = (
        f"{ctx['_sname']}\nFreq of Temp between {minv}"
        r"$^\circ$F and "
        f"{maxv}"
        r"$^\circ$F of NCEI-81 Average"
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)

    ax.plot(df.index.values, hvals, color="r", label="High", zorder=1)
    ax.plot(df.index.values, lvals, color="b", label="Low", zorder=1)
    ax.axhline(50, lw=2, color="green", zorder=2)
    ax.set_ylabel("Percentage of Years [%]")
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.legend(loc="best")
    ax.set_xlabel("* seven day smoother applied")
    ax.set_xlim(1, 367)
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    ax.set_ylim(0, 100)
    ax.grid(True)
    return fig, df
