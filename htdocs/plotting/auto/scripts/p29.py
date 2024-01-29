"""
This plot presents the frequency of a given hourly
variable being between two inclusive thresholds. The
hour is specified in UTC (Coordinated Universal Time) and observations
are rounded forward in time such that an observation at :54 after the
hour is moved to the top of the hour.  This autoplot attempts to consider only
one observation per hour.
"""
import calendar
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn, utc
from sqlalchemy import text

PDICT = {
    "tmpf": "Air Temperature [F]",
    "alti": "Altimeter [inch]",
    "dwpf": "Dew Point Temperature [F]",
    "feel": "Feels Like Temperature [F]",
    "relh": "Relative Humidity [%]",
    "mslp": "Sea Level Pressure [mb]",
    "vsby": "Visibility [miles]",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="AMW",
            label="Select Station:",
            network="IA_ASOS",
        ),
        dict(type="zhour", name="hour", default=20, label="At Time (UTC):"),
        {
            "type": "select",
            "name": "var",
            "default": "tmpf",
            "label": "Which Variable to Plot:",
            "options": PDICT,
        },
        dict(
            type="float",
            name="t1",
            default=70,
            label="Lower Bound [units of selected var] (inclusive):",
        ),
        dict(
            type="float",
            name="t2",
            default=79,
            label="Upper Bound [units of selected var] (inclusive):",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["zstation"]
    hour = ctx["hour"]
    t1 = ctx["t1"]
    t2 = ctx["t2"]
    params = {
        "station": station,
        "hour": hour,
        "t1": t1,
        "t2": t2,
    }
    varname = ctx["var"]
    varsql = {
        "tmpf": "round(tmpf::numeric, 0)",
        "dwpf": "round(dwpf::numeric, 0)",
        "feel": "round(feel::numeric, 0)",
    }
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            text(
                f"""
        WITH obs as (
            SELECT (valid + '10 minutes'::interval) at time zone 'UTC' as vld,
            {varsql.get(varname, varname)} as tmp from alldata
            WHERE station = :station and report_type = 3 and
            extract(hour from
                (valid + '10 minutes'::interval) at time zone 'UTC') = :hour
            and tmpf is not null
        )
        SELECT extract(month from vld) as month,
        sum(case when tmp >= :t1 and tmp <= :t2 then 1 else 0 end)::int
            as hits,
        sum(case when tmp > :t2 then 1 else 0 end) as above,
        sum(case when tmp < :t1 then 1 else 0 end) as below,
        count(*), max(vld) as max_utcvalid, min(vld) as min_utcvalid
        from obs GROUP by month ORDER by month ASC
        """
            ),
            conn,
            params=params,
            index_col="month",
        )
    if df.empty:
        raise NoDataFound("No Data Found.")
    df["freq"] = df["hits"] / df["count"] * 100.0
    df["above_freq"] = df["above"] / df["count"] * 100.0
    df["below_freq"] = df["below"] / df["count"] * 100.0
    ut = utc(2000, 1, 1, hour, 0)
    localt = ut.astimezone(ZoneInfo(ctx["_nt"].sts[station]["tzname"]))
    title = (
        f"{ctx['_sname']} ({df['min_utcvalid'].min().year}-"
        f"{df['max_utcvalid'].max().year})"
    )
    subtitle = (
        f"Frequency of {hour} UTC ({localt:%-I %p} LST) "
        f"{PDICT[varname]} between {t1} and {t2} (inclusive)"
    )
    fig = figure(title=title, subtitle=subtitle, apctx=ctx)
    ax = fig.add_axes([0.1, 0.23, 0.8, 0.67])
    ax.scatter(
        df.index.values,
        df["below_freq"],
        marker="s",
        s=40,
        label=f"Below {t1}",
        color="b",
        zorder=3,
    )
    bars = ax.bar(
        np.arange(1, 13),
        df["freq"],
        fc="tan",
        label=f"{t1} - {t2}",
        zorder=2,
        align="center",
    )
    ax.scatter(
        df.index.values,
        df["above_freq"],
        marker="s",
        s=40,
        label=f"Above {t2}",
        color="r",
        zorder=3,
    )
    for i, _bar in enumerate(bars):
        value = df.loc[i + 1, "hits"]
        label = f"{_bar.get_height():.1f}%"
        if value == 0:
            label = "None"
        ax.text(
            i + 1,
            _bar.get_height() + 3,
            label,
            ha="center",
            fontsize=12,
            zorder=4,
        )
    ax.set_xticks(range(0, 13))
    ax.set_xticklabels(calendar.month_abbr)
    ax.grid(True)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_ylabel("Frequency [%]")
    ax.set_xlim(0.5, 12.5)
    ax.legend(loc=(0.05, -0.18), ncol=3, fontsize=14)
    return fig, df


if __name__ == "__main__":
    plotter({})
