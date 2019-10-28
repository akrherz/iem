"""Max Dewpoint"""
import datetime
from collections import OrderedDict

from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

MDICT = OrderedDict(
    [
        ("all", "No Month/Time Limit"),
        ("spring", "Spring (MAM)"),
        ("fall", "Fall (SON)"),
        ("winter", "Winter (DJF)"),
        ("summer", "Summer (JJA)"),
        ("jan", "January"),
        ("feb", "February"),
        ("mar", "March"),
        ("apr", "April"),
        ("may", "May"),
        ("jun", "June"),
        ("jul", "July"),
        ("aug", "August"),
        ("sep", "September"),
        ("oct", "October"),
        ("nov", "November"),
        ("dec", "December"),
    ]
)

METRICS = OrderedDict(
    [("max_dwpf", "Max Dew Point (F)"), ("max_tmpf", "Max Air Temp (F)")]
)

DIRS = OrderedDict([("aoa", "At or Above"), ("below", "Below")])


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """This application plots the number of days for a
    given month or period of months that a given variable was above or below
    some threshold.
    """
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="AMW",
            network="IA_ASOS",
            label="Select Station:",
        ),
        dict(
            type="select",
            name="var",
            default="max_dwpf",
            label="Which Variable",
            options=METRICS,
        ),
        dict(
            type="select",
            name="dir",
            default="aoa",
            label="Threshold Direction:",
            options=DIRS,
        ),
        dict(type="int", name="thres", default=65, label="Threshold"),
        dict(
            type="select",
            name="month",
            default="all",
            label="Month Limiter",
            options=MDICT,
        ),
        dict(
            type="year",
            min=1928,
            default=datetime.date.today().year,
            label="Year to Highlight",
            name="year",
        ),
    ]
    return desc


def get_context(fdict):
    """Do the processing work"""
    pgconn = get_dbconn("iem")
    ctx = get_autoplot_context(fdict, get_description())

    station = ctx["zstation"]
    month = ctx["month"]
    varname = ctx["var"]
    mydir = ctx["dir"]
    threshold = ctx["thres"]

    offset = "day"
    if month == "all":
        months = range(1, 13)
    elif month == "fall":
        months = [9, 10, 11]
    elif month == "winter":
        months = [12, 1, 2]
        offset = "day + '1 month'::interval"
    elif month == "spring":
        months = [3, 4, 5]
    elif month == "summer":
        months = [6, 7, 8]
    else:
        ts = datetime.datetime.strptime("2000-" + month + "-01", "%Y-%b-%d")
        # make sure it is length two for the trick below in SQL
        months = [ts.month, 999]

    opp = ">=" if mydir == "aoa" else "<"
    ctx["df"] = read_sql(
        """
        SELECT extract(year from """
        + offset
        + """)::int as year,
        sum(case when """
        + varname
        + """::int """
        + opp
        + """ %s
            then 1 else 0 end)
        as count
        from summary s JOIN stations t on (s.iemid = t.iemid)
        WHERE t.id = %s and t.network = %s and extract(month from day) in %s
        GROUP by year ORDER by year ASC
        """,
        pgconn,
        params=(threshold, station, ctx["network"], tuple(months)),
        index_col="year",
    )
    ctx["title"] = "(%s) %s %s %.0f" % (
        MDICT[ctx["month"]],
        METRICS[ctx["var"]],
        DIRS[ctx["dir"]],
        ctx["thres"],
    )
    ctx["subtitle"] = "%s [%s]" % (
        ctx["_nt"].sts[ctx["zstation"]]["name"],
        ctx["zstation"],
    )
    return ctx


def highcharts(fdict):
    """Highcharts output"""
    ctx = get_context(fdict)
    ctx["df"].reset_index(inplace=True)
    data = ctx["df"][["year", "count"]].to_json(orient="values")

    return (
        """
    $("#ap_container").highcharts({
        chart: {
            type: 'column'
        },
        yAxis: {title: {text: 'Days'}},
        title: {text: '"""
        + ctx["title"]
        + """'},
        subtitle: {text: '"""
        + ctx["subtitle"]
        + """'},
        series: [{
            name: 'Days',
            data: """
        + data
        + """
        }]
    });
    """
    )


def plotter(fdict):
    """ Go """
    ctx = get_context(fdict)
    df = ctx["df"]
    if df.empty:
        raise NoDataFound("Error, no results returned!")

    (fig, ax) = plt.subplots(1, 1)
    ax.set_title("%s\n%s" % (ctx["title"], ctx["subtitle"]))
    ax.bar(
        df.index.values, df["count"], align="center", fc="green", ec="green"
    )
    if ctx["year"] in df.index:
        ax.bar(
            ctx["year"],
            df.at[ctx["year"], "count"],
            align="center",
            fc="red",
            ec="red",
            zorder=5,
        )
    ax.grid(True)
    ax.set_ylabel("Days Per Period")
    ax.set_xlim(df.index.min() - 0.5, df.index.max() + 0.5)
    avgv = df["count"].mean()
    ax.axhline(avgv)
    ax.text(df.index.max() + 1, avgv, "%.1f" % (avgv,))
    return fig, df


if __name__ == "__main__":
    plotter(dict(network="IA_ASOS", station="AMW"))
