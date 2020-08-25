"""Simple stats by year"""
import datetime
from collections import OrderedDict

import numpy as np
from pandas.io.sql import read_sql
from pyiem import network, util
from pyiem.plot.use_agg import plt
from pyiem.exceptions import NoDataFound

PDICT = OrderedDict(
    [
        ("max-high", "Maximum High"),
        ("avg-high", "Average High"),
        ("min-high", "Minimum High"),
        ("max-low", "Maximum Low"),
        ("avg-low", "Average Low"),
        ("min-low", "Minimum Low"),
        ("max-precip", "Maximum Daily Precip"),
        ("range-hilo", "Range between Min Low and Max High"),
        ("sum-precip", "Total Precipitation"),
        ("avg-precip", "Daily Average Precipitation"),
        ("avg-precip2", "Daily Average Precipitation (on wet days)"),
        ("days-precip", "Days with Precipitation Above (threshold)"),
        (
            "days-high-above",
            "Days with High Temp Greater Than or Equal To (threshold)",
        ),
        (
            "days-lows-above",
            "Days with Low Temp Greater Than or Equal To (threshold)",
        ),
        ("days-lows-below", "Days with Low Temp Below (threshold)"),
    ]
)


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc[
        "description"
    ] = """This plot displays a metric for each year.
    In most cases, you can access the raw data for these plots
    <a href="/climodat/" class="alert-link">here.</a>"""
    desc["data"] = True
    eyear = datetime.date.today().year
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IA0000",
            network="IACLIMATE",
            label="Select Station",
        ),
        dict(
            type="select",
            name="type",
            default="max-high",
            label="Which metric to plot?",
            options=PDICT,
        ),
        dict(
            type="float",
            name="threshold",
            default=-99,
            label="Threshold (optional, specify when appropriate):",
        ),
        dict(
            type="year",
            name="syear",
            default=1893,
            label="Start Year of Plot: (inclusive)",
        ),
        dict(
            type="year",
            name="eyear",
            default=eyear,
            label="Start Year of Plot: (inclusive)",
        ),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = util.get_dbconn("coop")

    ctx = util.get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    threshold = ctx["threshold"]
    ptype = ctx["type"]
    syear = ctx["syear"]
    eyear = ctx["eyear"]

    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))
    if station not in nt.sts:
        raise NoDataFound("Unknown station metadata.")

    df = read_sql(
        f"""
    SELECT year,
    max(high) as "max-high",
    min(high) as "min-high",
    avg(high) as "avg-high",
    max(low) as "max-low",
    min(low) as "min-low",
    avg(low) as "avg-low",
    max(precip) as "max-precip",
    sum(precip) as "sum-precip",
    sum(case when high >= %s then 1 else 0 end) as "days-high-above",
    sum(case when low >= %s then 1 else 0 end) as "days-lows-above",
    sum(case when low < %s then 1 else 0 end) as "days-lows-below",
    avg(precip) as "avg-precip",
    avg(case when precip >= 0.01 then precip else null end) as "avg-precip2",
    sum(case when precip >= %s then 1 else 0 end) as "days-precip"
    from {table}
    where station = %s and year >= %s and year <= %s
    GROUP by year ORDER by year ASC
    """,
        pgconn,
        params=(
            threshold,
            threshold,
            threshold,
            threshold,
            station,
            syear,
            eyear,
        ),
        index_col="year",
    )
    if df.empty:
        raise NoDataFound("No Data Found.")
    df["range-hilo"] = df["max-high"] - df["min-low"]

    (fig, ax) = plt.subplots(1, 1)
    avgv = df[ptype].mean()
    data = df[ptype].values
    years = df.index.values

    # Compute 30 year trailing average
    tavg = [None] * 30
    for i in range(30, len(data)):
        tavg.append(np.average(data[i - 30 : i]))

    a1981_2010 = df.loc[1981:2011, ptype].mean()

    colorabove = "tomato"
    colorbelow = "dodgerblue"
    precision = "%.1f"
    if ptype in [
        "max-precip",
        "sum-precip",
        "avg-precip",
        "avg-precip2",
        "days-precip",
    ]:
        colorabove = "dodgerblue"
        colorbelow = "tomato"
        precision = "%.2f"
    bars = ax.bar(np.array(years) - 0.4, data, fc=colorabove, ec=colorabove)
    for i, mybar in enumerate(bars):
        if data[i] < avgv:
            mybar.set_facecolor(colorbelow)
            mybar.set_edgecolor(colorbelow)
    lbl = "Avg: " + precision % (avgv,)
    ax.axhline(avgv, lw=2, color="k", zorder=2, label=lbl)
    lbl = "1981-2010: " + precision % (a1981_2010,)
    ax.axhline(a1981_2010, lw=2, color="brown", zorder=2, label=lbl)
    ax.plot(years, tavg, lw=1.5, color="g", zorder=4, label="Trailing 30yr")
    ax.plot(years, tavg, lw=3, color="yellow", zorder=3)
    ax.set_xlim(years[0] - 1, years[-1] + 1)
    if ptype.find("precip") == -1 and ptype.find("days") == -1:
        ax.set_ylim(min(data) - 5, max(data) + 5)

    ax.set_xlabel("Year")
    units = r"$^\circ$F"
    if ptype.find("days") > 0:
        units = "days"
    elif ptype.find("precip") > 0:
        units = "inches"
    ax.set_ylabel("%s [%s]" % (PDICT[ptype], units))
    ax.grid(True)
    ax.legend(ncol=3, loc="best", fontsize=10)
    msg = ("[%s] %s %s-%s %s") % (
        station,
        nt.sts[station]["name"],
        min(years),
        max(years),
        PDICT[ptype],
    )
    if ptype.find("days") == 0:
        msg += " (%s)" % (threshold,)
    tokens = msg.split()
    sz = int(len(tokens) / 2)
    ax.set_title(" ".join(tokens[:sz]) + "\n" + " ".join(tokens[sz:]))

    return fig, df


if __name__ == "__main__":
    plotter(dict())
