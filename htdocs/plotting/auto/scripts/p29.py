"""Hourly temp ranges"""
import calendar

import pytz
import numpy as np
from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn, utc
from pyiem.exceptions import NoDataFound


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc[
        "description"
    ] = """This plot presents the frequency of a given hourly
    temperature being within the bounds of two temperature thresholds. The
    hour is specified in UTC (Coordinated Universal Time) and observations
    are rounded forward in time such that an observation at :54 after the
    hour is moved to the top of the hour.
    """
    desc["data"] = True
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="AMW",
            label="Select Station:",
            network="IA_ASOS",
        ),
        dict(type="zhour", name="hour", default=20, label="At Time (UTC):"),
        dict(
            type="int",
            name="t1",
            default=70,
            label="Lower Temperature Bound (inclusive):",
        ),
        dict(
            type="int",
            name="t2",
            default=79,
            label="Upper Temperature Bound (inclusive):",
        ),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn("asos")
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["zstation"]
    hour = ctx["hour"]
    t1 = ctx["t1"]
    t2 = ctx["t2"]

    df = read_sql(
        """
    WITH obs as (
        SELECT date_trunc('hour', valid) as t,
        round(avg(tmpf)::numeric, 0) as tmp from alldata
        WHERE station = %s and (extract(minute from valid) > 50 or
        extract(minute from valid) = 10) and
        extract(hour from valid at time zone 'UTC') = %s and tmpf is not null
        GROUP by t
    )
    SELECT extract(month from t) as month,
    sum(case when tmp >= %s and tmp <= %s then 1 else 0 end)::int as hits,
    sum(case when tmp > %s then 1 else 0 end) as above,
    sum(case when tmp < %s then 1 else 0 end) as below,
    count(*) from obs GROUP by month ORDER by month ASC
    """,
        pgconn,
        params=(station, hour, t1, t2, t2, t1),
        index_col="month",
    )
    if df.empty:
        raise NoDataFound("No Data Found.")
    df["freq"] = df["hits"] / df["count"] * 100.0
    df["above_freq"] = df["above"] / df["count"] * 100.0
    df["below_freq"] = df["below"] / df["count"] * 100.0
    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))
    ax.scatter(
        df.index.values,
        df["below_freq"],
        marker="s",
        s=40,
        label="Below %s" % (t1,),
        color="b",
        zorder=3,
    )
    bars = ax.bar(
        np.arange(1, 13),
        df["freq"],
        fc="tan",
        label="%s - %s" % (t1, t2),
        zorder=2,
        align="center",
    )
    ax.scatter(
        df.index.values,
        df["above_freq"],
        marker="s",
        s=40,
        label="Above %s" % (t2,),
        color="r",
        zorder=3,
    )
    for i, _bar in enumerate(bars):
        value = df.loc[i + 1, "hits"]
        label = "%.1f%%" % (_bar.get_height(),)
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
    ut = utc(2000, 1, 1, hour, 0)
    localt = ut.astimezone(pytz.timezone(ctx["_nt"].sts[station]["tzname"]))
    ax.set_xlim(0.5, 12.5)
    ax.set_title(
        (
            "%s [%s]\nFrequency of %s UTC (%s LST) "
            r"Temp between %s$^\circ$F and %s$^\circ$F"
        )
        % (
            ctx["_nt"].sts[station]["name"],
            station,
            hour,
            localt.strftime("%-I %p"),
            t1,
            t2,
        )
    )
    ax.legend(loc=(0.05, -0.14), ncol=3, fontsize=14)
    pos = ax.get_position()
    ax.set_position([pos.x0, pos.y0 + 0.07, pos.width, pos.height * 0.93])
    return fig, df


if __name__ == "__main__":
    plotter(dict())
