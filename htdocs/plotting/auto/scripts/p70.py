"""period between first and last watch"""
import datetime

from pandas.io.sql import read_sql
import numpy as np
from matplotlib.ticker import FormatStrFormatter
from pyiem import reference
from pyiem.plot.use_agg import plt
from pyiem.nws import vtec
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = {"jan1": "January 1", "jul1": "July 1"}
PDICT2 = {
    "wfo": "View by Single NWS Forecast Office",
    "state": "View by State",
}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """
    This chart attempts to display the period between the first and last VTEC
    enabled watch, warning or advisory <strong>issuance</strong> by year.  For
    some long term products, like Flood Warnings, this plot does not attempt
    to show the time domain that those products were valid, only the issuance.
    The individual ticks within the bars on the left hand side plot are
    individual dates during the period that had an issuance event.  The right
    two plots display the total number of events and the total number of dates
    with at least one event.</p>

    <p>For the purposes of this plot, an event is defined by a single VTEC
    event identifier usage.  For example, a single Tornado Watch covering
    10 counties only counts as one event. The simple average is computed
    over the years excluding the first and last year.</p>

    <p>When you split this plot by 1 July, the year shown is for the year of
    the second half of this period, ie 2020 is 1 Jul 2019 - 30 Jun 2020.</p>
    """
    desc["arguments"] = [
        dict(
            type="select",
            name="opt",
            default="wfo",
            options=PDICT2,
            label="View by WFO or State?",
        ),
        dict(
            type="networkselect",
            name="station",
            network="WFO",
            default="DMX",
            label="Select WFO:",
        ),
        dict(type="state", default="IA", name="state", label="Select State:"),
        dict(
            type="phenomena",
            name="phenomena",
            default="SV",
            label="Select Watch/Warning Phenomena Type:",
        ),
        dict(
            type="significance",
            name="significance",
            default="W",
            label="Select Watch/Warning Significance Level:",
        ),
        dict(
            type="select",
            options=PDICT,
            label="Split the year on date:",
            default="jan1",
            name="split",
        ),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn("postgis")
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"][:4]
    phenomena = ctx["phenomena"]
    significance = ctx["significance"]
    split = ctx["split"]
    opt = ctx["opt"]
    state = ctx["state"]

    wfolimiter = " wfo = '%s' " % (station,)
    if opt == "state":
        wfolimiter = " substr(ugc, 1, 2) = '%s' " % (state,)

    df = read_sql(
        f"""WITH data as (
            SELECT eventid, extract(year from issue) as year,
            min(date(issue)) as date from warnings where {wfolimiter}
            and phenomena = %s and significance = %s GROUP by eventid, year)
        SELECT year::int, date, count(*) from data GROUP by year, date
        ORDER by year ASC, date ASC
        """,
        pgconn,
        params=(phenomena, significance),
        index_col=None,
    )
    if df.empty:
        raise NoDataFound("No data found for query")

    # Since many VTEC events start in 2005, we should not trust any
    # data that has its first year in 2005
    if df["year"].min() == 2005:
        df = df[df["year"] > 2005]
    # Split the season at jul 1, if requested
    if split == "jul1":
        df["year"] = df.apply(
            lambda x: x["year"] + 1 if x["date"].month > 6 else x["year"],
            axis=1,
        )
        df["doy"] = df.apply(
            lambda x: x["date"] - datetime.date(x["year"] - 1, 7, 1), axis=1
        )
    else:
        df["doy"] = df.apply(
            lambda x: x["date"] - datetime.date(x["year"], 1, 1), axis=1
        )
    df["doy"] = df["doy"].dt.days

    fig = plt.figure(figsize=(12.0, 6.75))
    ax = plt.axes([0.07, 0.1, 0.65, 0.8])

    for year, gdf in df.groupby("year"):
        size = gdf["doy"].max() - gdf["doy"].min()
        if size < 1:
            size = 1
        ax.barh(
            year,
            size,
            left=gdf["doy"].min(),
            ec="brown",
            fc="tan",
            align="center",
        )
        ax.barh(
            gdf["year"].values,
            [1] * len(gdf.index),
            left=gdf["doy"].values,
            color="blue",
            zorder=3,
        )
    gdf = df[["year", "doy"]].groupby("year").agg(["min", "max"])
    # Exclude first and last year in the average
    avg_start = np.average(gdf["doy", "min"].values[1:-1])
    avg_end = np.average(gdf["doy", "max"].values[1:-1])
    ax.axvline(avg_start, lw=2, color="k")
    ax.axvline(avg_end, lw=2, color="k")
    x0 = datetime.date(2000, 1 if split == "jan1" else 7, 1)
    ax.set_xlabel(
        ("Average Start Date: %s, End Date: %s")
        % (
            (x0 + datetime.timedelta(days=int(avg_start))).strftime("%-d %b"),
            (x0 + datetime.timedelta(days=int(avg_end))).strftime("%-d %b"),
        )
    )
    title = "[%s] NWS %s" % (station, ctx["_nt"].sts[station]["name"])
    if opt == "state":
        title = ("NWS Issued Alerts for State of %s") % (
            reference.state_names[state],
        )
    ax.set_title(
        ("%s\nPeriod between First and Last %s (%s.%s)")
        % (
            title,
            vtec.get_ps_string(phenomena, significance),
            phenomena,
            significance,
        )
    )
    ax.grid()
    xticks = []
    xticklabels = []
    for i in range(367):
        date = x0 + datetime.timedelta(days=i)
        if date.day == 1:
            xticks.append(i)
            xticklabels.append(date.strftime("%b"))
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.set_xlim(df["doy"].min() - 10, df["doy"].max() + 10)
    ax.set_ylabel("Year")
    ax.set_ylim(df["year"].min() - 0.5, df["year"].max() + 0.5)
    xFormatter = FormatStrFormatter("%d")
    ax.yaxis.set_major_formatter(xFormatter)

    # ______________________________________________
    ax = plt.axes([0.75, 0.1, 0.1, 0.8])
    gdf = df[["year", "count"]].groupby("year").sum()
    ax.barh(gdf.index.values, gdf["count"].values, fc="blue", align="center")
    ax.set_ylim(df["year"].min() - 0.5, df["year"].max() + 0.5)
    plt.setp(ax.get_yticklabels(), visible=False)
    ax.grid(True)
    ax.set_xlabel("# Events")
    ax.yaxis.set_major_formatter(xFormatter)
    xloc = plt.MaxNLocator(3)
    ax.xaxis.set_major_locator(xloc)

    # __________________________________________
    ax = plt.axes([0.88, 0.1, 0.1, 0.8])
    gdf = df[["year", "count"]].groupby("year").count()
    ax.barh(gdf.index.values, gdf["count"].values, fc="blue", align="center")
    ax.set_ylim(df["year"].min() - 0.5, df["year"].max() + 0.5)
    plt.setp(ax.get_yticklabels(), visible=False)
    ax.grid(True)
    ax.set_xlabel("# Dates")
    ax.yaxis.set_major_formatter(xFormatter)
    xloc = plt.MaxNLocator(3)
    ax.xaxis.set_major_locator(xloc)

    return fig, df


if __name__ == "__main__":
    plotter(dict(split="jul1"))
