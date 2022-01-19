"""period between first and last watch"""
import datetime

from pandas.io.sql import read_sql
import numpy as np
from matplotlib.ticker import FormatStrFormatter
import matplotlib.colors as mpcolors
from matplotlib.colorbar import ColorbarBase
from pyiem import reference
from pyiem.plot import get_cmap, figure
from pyiem.plot.use_agg import plt
from pyiem.nws import vtec
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = {"jan1": "January 1", "jul1": "July 1"}
PDICT2 = {
    "wfo": "View by Single NWS Forecast Office",
    "state": "View by State",
}
PDICT3 = {
    "daily": "Color bars with daily issuance totals",
    "accum": "Color bars with accumulated year to date totals",
    "none": "Bars should not be colored, please",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """
    This chart attempts to display the period between the first and last VTEC
    enabled watch, warning or advisory <strong>issuance</strong> by year.  For
    some long term products, like Flood Warnings, this plot does not attempt
    to show the time domain that those products were valid, only the issuance.
    The right two plots display the total number of events and the total
    number of dates with at least one event.</p>

    <p>The left plot can be colorized by either coloring the event counts per
    day or the accumulated "year/season to date" total.</p>

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
        dict(
            type="select",
            options=PDICT3,
            label="How to color bars for left plot:",
            default="daily",
            name="f",
        ),
        dict(type="cmap", name="cmap", default="jet", label="Color Ramp:"),
    ]
    return desc


def plotter(fdict):
    """Go"""
    pgconn = get_dbconn("postgis")
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"][:4]
    phenomena = ctx["phenomena"]
    significance = ctx["significance"]
    split = ctx["split"]
    opt = ctx["opt"]
    state = ctx["state"]

    wfolimiter = f" wfo = '{station}' "
    if opt == "state":
        wfolimiter = f" substr(ugc, 1, 2) = '{state}' "

    df = read_sql(
        f"""WITH data as (
            SELECT eventid, wfo, extract(year from issue) as year,
            min(date(issue)) as date from warnings where {wfolimiter}
            and phenomena = %s and significance = %s
            GROUP by eventid, wfo, year)
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

    title = f"[{station}] NWS {ctx['_nt'].sts[station]['name']}"
    if opt == "state":
        title = (
            f"NWS Issued Alerts for State of {reference.state_names[state]}"
        )
    title += (
        "\n"
        "Period between First and Last "
        f"{vtec.get_ps_string(phenomena, significance)} "
        f"({phenomena}.{significance})"
    )

    fig = figure(apctx=ctx, title=title)
    ax = fig.add_axes([0.12, 0.1, 0.61, 0.8])

    # Create a color bar for the number of events per day
    cmap = get_cmap(ctx["cmap"])
    cmap.set_under("tan")
    cmap.set_over("black")
    bins = [1, 2, 3, 4, 5, 7, 10, 15, 20, 25, 50]
    if ctx["f"] == "accum":
        maxval = int(df[["year", "count"]].groupby("year").sum().max()) + 1
        if maxval < 11:
            bins = np.arange(1, 11)
        elif maxval < 21:
            bins = np.arange(1, 21)
        else:
            bins = np.linspace(1, maxval, 20, dtype="i")

    norm = mpcolors.BoundaryNorm(bins, cmap.N)
    if ctx["f"] != "none":
        cax = fig.add_axes(
            [0.01, 0.12, 0.02, 0.6], frameon=False, yticks=[], xticks=[]
        )
        cb = ColorbarBase(
            cax, norm=norm, cmap=cmap, extend="max", spacing="proportional"
        )
        cb.set_label(
            "Daily Count" if ctx["f"] == "daily" else "Accum Count",
            loc="bottom",
        )

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
        if ctx["f"] == "none":
            continue
        elif ctx["f"] == "daily":
            ax.barh(
                gdf["year"].values,
                [1] * len(gdf.index),
                left=gdf["doy"].values,
                zorder=3,
                color=cmap(norm([gdf["count"]]))[0],
            )
            continue
        # Do the fancy pants accum
        gdf["cumsum"] = gdf["count"].cumsum()
        ax.barh(
            gdf["year"].values[::-1],
            gdf["doy"].values[::-1] - gdf["doy"].values[0] + 1,
            left=[gdf["doy"].values[0]] * len(gdf.index),
            zorder=3,
            color=cmap(norm([gdf["cumsum"].values[::-1]]))[0],
        )
    gdf = df[["year", "doy"]].groupby("year").agg(["min", "max"])
    # Exclude first and last year in the average
    avg_start = np.average(gdf["doy", "min"].values[1:-1])
    avg_end = np.average(gdf["doy", "max"].values[1:-1])
    ax.axvline(avg_start, ls=":", lw=2, color="k")
    ax.axvline(avg_end, ls=":", lw=2, color="k")
    x0 = datetime.date(2000, 1 if split == "jan1" else 7, 1)
    _1 = (x0 + datetime.timedelta(days=int(avg_start))).strftime("%-d %b")
    _2 = (x0 + datetime.timedelta(days=int(avg_end))).strftime("%-d %b")
    ax.set_xlabel(f"Average Start Date: {_1}, End Date: {_2}")
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
    ax = fig.add_axes([0.75, 0.1, 0.1, 0.8])
    gdf = df[["year", "count"]].groupby("year").sum()
    ax.barh(
        gdf.index.values,
        gdf["count"].values,
        color="blue" if ctx["f"] != "accum" else cmap(norm([gdf["count"]]))[0],
        align="center",
    )
    ax.set_ylim(df["year"].min() - 0.5, df["year"].max() + 0.5)
    plt.setp(ax.get_yticklabels(), visible=False)
    ax.grid(True)
    ax.set_xlabel("# Events")
    ax.yaxis.set_major_formatter(xFormatter)
    xloc = plt.MaxNLocator(3)
    ax.xaxis.set_major_locator(xloc)

    # __________________________________________
    ax = fig.add_axes([0.88, 0.1, 0.1, 0.8])
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
    plotter(dict(split="jul1", f="accum"))
