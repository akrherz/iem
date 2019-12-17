"""Binned"""
import datetime
import calendar

from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = {"tmpf": "Air Temperature", "dwpf": "Dew Point Temperature"}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["cache"] = 86400
    desc[
        "description"
    ] = """This plot is a histogram of observed temperatures
    placed into six range bins of your choice.  The plot attempts to answer
    the question of how often is the air temperature within a certain range
    during a certain time of the year.  The data for this plot is partitioned
    by week of the year.  Each plot legend entry contains the overall
    frequency for that bin."""
    desc["data"] = True
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="DSM",
            network="IA_ASOS",
            label="Select Station:",
        ),
        dict(
            type="select",
            options=PDICT,
            default="tmpf",
            name="var",
            label="Select temperature to plot:",
        ),
        dict(
            type="int",
            name="t1",
            default=0,
            label="Temperature Threshold #1 (lowest)",
        ),
        dict(
            type="int", name="t2", default=32, label="Temperature Threshold #2"
        ),
        dict(
            type="int", name="t3", default=50, label="Temperature Threshold #3"
        ),
        dict(
            type="int", name="t4", default=70, label="Temperature Threshold #4"
        ),
        dict(
            type="int",
            name="t5",
            default=90,
            label="Temperature Threshold #5 (highest)",
        ),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn("asos")
    ctx = get_autoplot_context(fdict, get_description())

    station = ctx["zstation"]
    t1 = ctx["t1"]
    t2 = ctx["t2"]
    t3 = ctx["t3"]
    t4 = ctx["t4"]
    t5 = ctx["t5"]
    v = ctx["var"]

    df = read_sql(
        """
        SELECT extract(week from valid) as week,
        sum(case when """
        + v
        + """::int < %s then 1 else 0 end) as d1,
        sum(case when """
        + v
        + """::int < %s and """
        + v
        + """::int >= %s then 1 else 0 end) as d2,
        sum(case when """
        + v
        + """::int < %s and """
        + v
        + """::int >= %s then 1 else 0 end) as d3,
        sum(case when """
        + v
        + """::int < %s and """
        + v
        + """::int >= %s then 1 else 0 end) as d4,
        sum(case when """
        + v
        + """::int < %s and """
        + v
        + """::int >= %s then 1 else 0 end) as d5,
        sum(case when """
        + v
        + """::int >= %s then 1 else 0 end) as d6,
        count(*)
        from alldata where station = %s and """
        + v
        + """ is not null
        and extract(minute  from valid  - '1 minute'::interval) > 49
        and report_type = 2
        GROUP by week ORDER by week ASC
    """,
        pgconn,
        params=(t1, t2, t1, t3, t2, t4, t3, t5, t4, t5, station),
        index_col="week",
    )
    if df.empty:
        raise NoDataFound("No observations found for query.")

    for i in range(1, 7):
        df["p%s" % (i,)] = df["d%s" % (i,)] / df["count"] * 100.0
    sts = datetime.datetime(2012, 1, 1)
    xticks = []
    for i in range(1, 13):
        ts = sts.replace(month=i)
        xticks.append(float(ts.strftime("%j")) / 7.0)

    (fig, ax) = plt.subplots(1, 1)
    x = df.index.values - 1
    val = df["d6"].sum() / df["count"].sum() * 100.0
    ax.bar(
        x,
        df["p6"].values,
        bottom=(df["p5"] + df["p4"] + df["p3"] + df["p2"] + df["p1"]).values,
        width=1,
        fc="red",
        ec="None",
        label="%s & Above (%.1f%%)" % (t5, val),
    )
    val = df["d5"].sum() / df["count"].sum() * 100.0
    ax.bar(
        x,
        df["p5"].values,
        bottom=(df["p4"] + df["p3"] + df["p2"] + df["p1"]).values,
        width=1,
        fc="tan",
        ec="None",
        label="%s-%s (%.1f%%)" % (t4, t5 - 1, val),
    )
    val = df["d4"].sum() / df["count"].sum() * 100.0
    ax.bar(
        x,
        df["p4"].values,
        bottom=(df["p3"] + df["p2"] + df["p1"]).values,
        width=1,
        fc="yellow",
        ec="None",
        label="%s-%s (%.1f%%)" % (t3, t4 - 1, val),
    )
    val = df["d3"].sum() / df["count"].sum() * 100.0
    ax.bar(
        x,
        df["p3"].values,
        width=1,
        fc="green",
        bottom=(df["p2"] + df["p1"]).values,
        ec="None",
        label="%s-%s (%.1f%%)" % (t2, t3 - 1, val),
    )
    val = df["d2"].sum() / df["count"].sum() * 100.0
    ax.bar(
        x,
        df["p2"].values,
        bottom=df["p1"].values,
        width=1,
        fc="blue",
        ec="None",
        label="%s-%s (%.1f%%)" % (t1, t2 - 1, val),
    )
    val = df["d1"].sum() / df["count"].sum() * 100.0
    ax.bar(
        x,
        df["p1"].values,
        width=1,
        fc="purple",
        ec="None",
        label="Below %s (%.1f%%)" % (t1, val),
    )

    ax.grid(True, zorder=11)
    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    ax.set_title(
        ("%s [%s]\n" r"Hourly %s ($^\circ$F) Frequencies (%s-%s)")
        % (
            ctx["_nt"].sts[station]["name"],
            station,
            PDICT[v],
            ab.year,
            datetime.datetime.now().year,
        )
    )
    ax.set_ylabel("Frequency [%]")

    ax.set_xticks(xticks)
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(0, 53)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 10, 25, 50, 75, 90, 100])

    # Shrink current axis's height by 10% on the bottom
    box = ax.get_position()
    ax.set_position(
        [box.x0, box.y0 + box.height * 0.2, box.width, box.height * 0.8]
    )

    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.1),
        fancybox=True,
        shadow=True,
        ncol=3,
        scatterpoints=1,
        fontsize=12,
    )

    return fig, df


if __name__ == "__main__":
    plotter(dict())
