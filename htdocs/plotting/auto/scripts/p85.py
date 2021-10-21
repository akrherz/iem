"""Hourly Temp Frequencies"""
import calendar
from collections import OrderedDict

from pandas.io.sql import read_sql
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.plot.use_agg import plt
from pyiem.exceptions import NoDataFound

PDICT = OrderedDict(
    [("above", "At or Above Temperature"), ("below", "Below Temperature")]
)


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc[
        "description"
    ] = """Based on IEM archives of METAR reports, this
    application produces the hourly frequency of a temperature at or
    above or below a temperature thresold."""
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="AMW",
            network="IA_ASOS",
            label="Select Station:",
        ),
        dict(type="month", name="month", default=7, label="Month:"),
        dict(
            type="int",
            name="t",
            default=80,
            label="Temperature Threshold (F):",
        ),
        dict(
            type="select",
            name="dir",
            default="above",
            label="Threshold Option:",
            options=PDICT,
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    pgconn = get_dbconn("asos", user="nobody")

    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["zstation"]
    month = int(ctx["month"])
    thres = ctx["t"]
    mydir = ctx["dir"]

    tzname = ctx["_nt"].sts[station]["tzname"]

    df = read_sql(
        """
    WITH data as (
        SELECT valid at time zone %s  + '10 minutes'::interval as v, tmpf
        from alldata where station = %s and tmpf > -90 and tmpf < 150
        and extract(month from valid) = %s and report_type = 2)

    SELECT extract(hour from v) as hour,
    min(v) as min_valid, max(v) as max_valid,
    sum(case when tmpf::int < %s THEN 1 ELSE 0 END) as below,
    sum(case when tmpf::int >= %s THEN 1 ELSE 0 END) as above,
    count(*) from data
    GROUP by hour ORDER by hour ASC
    """,
        pgconn,
        params=(tzname, station, month, thres, thres),
        index_col="hour",
    )
    if df.empty:
        raise NoDataFound("No data found.")

    df["below_freq"] = df["below"].values.astype("f") / df["count"] * 100.0
    df["above_freq"] = df["above"].values.astype("f") / df["count"] * 100.0

    freq = df[mydir + "_freq"].values
    hours = df.index.values

    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))
    bars = ax.bar(hours, freq, fc="blue", align="center")
    for i, mybar in enumerate(bars):
        ax.text(
            i,
            mybar.get_height() + 3,
            "%.0f" % (mybar.get_height(),),
            ha="center",
            fontsize=10,
        )
    ax.set_xticks(range(0, 25, 3))
    ax.set_xticklabels(
        ["Mid", "3 AM", "6 AM", "9 AM", "Noon", "3 PM", "6 PM", "9 PM", "Mid"]
    )
    ax.grid(True)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_ylabel("Frequency [%]")
    ax.set_xlabel(f"Hour Timezone: {tzname}")
    ax.set_xlim(-0.5, 23.5)
    ax.set_title(
        ("(%s - %s) %s [%s]\n" r"Frequency of %s Hour, %s: %s$^\circ$F")
        % (
            df["min_valid"].min().year,
            df["max_valid"].max().year,
            ctx["_nt"].sts[station]["name"],
            station,
            calendar.month_name[month],
            PDICT[mydir],
            thres,
        )
    )

    return fig, df


if __name__ == "__main__":
    plotter(dict())
