"""temperature above average frequency by year"""
from collections import OrderedDict
import datetime

import matplotlib.patheffects as PathEffects
from pandas.io.sql import read_sql
from pyiem import network
from pyiem.plot.use_agg import plt
from pyiem.plot.util import fitbox
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = {
    "high": "High Temperature",
    "low": "Low Temperature",
    "avg": "Average Temperature",
}
PDICT2 = {
    "degrees": "Degrees Fahrenheit",
    "sigma": "Sigma (1 Standard Deviation)",
}
PDICT3 = {"above": "Above", "below": "Below"}
PDICT4 = {"percent": "Percentage", "number": "Number"}
MDICT = OrderedDict(
    [
        ("all", "No Month/Season Limit"),
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


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc[
        "description"
    ] = """The frequency of days per year that the temperature
    was above/below average.  Data is shown for the current year as well, so
    you should consider the representativity of that value when compared with
    other years with a full year's worth of data."""
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IA0000",
            label="Select Station",
            network="IACLIMATE",
        ),
        dict(
            type="select",
            options=PDICT,
            name="var",
            default="high",
            label="Which variable to plot?",
        ),
        dict(
            type="select",
            options=PDICT3,
            name="which",
            default="above",
            label="Compute above or below average:",
        ),
        dict(
            type="select",
            options=PDICT2,
            name="unit",
            default="degrees",
            label="How to measure departure from average:",
        ),
        dict(
            type="float",
            name="mag",
            default=0,
            label="Absolute magnitude of departure expressed with previous:",
        ),
        dict(
            type="select",
            name="month",
            default="all",
            label="Month Limiter",
            options=MDICT,
        ),
        dict(
            type="select",
            name="opt",
            default="percent",
            label="Express days as percentage or number of",
            options=PDICT4,
        ),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn("coop")
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    varname = ctx["var"]
    month = ctx["month"]
    ctx["mag"] = abs(ctx["mag"])

    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))

    yr = "year as yr"
    if month == "all":
        months = range(1, 13)
    elif month == "fall":
        months = [9, 10, 11]
    elif month == "winter":
        months = [12, 1, 2]
        yr = "extract(year from o.day - '60 days'::interval) as yr"
    elif month == "spring":
        months = [3, 4, 5]
    elif month == "summer":
        months = [6, 7, 8]
    else:
        ts = datetime.datetime.strptime("2000-" + month + "-01", "%Y-%b-%d")
        # make sure it is length two for the trick below in SQL
        months = [ts.month, 999]

    metric = ""
    smul = 0
    offset = 0
    if ctx["mag"] > 0:
        if ctx["unit"] == "sigma":
            metric = fr"{ctx['mag']}$\sigma$"
            smul = ctx["mag"]
        elif ctx["unit"] == "degrees":
            metric = fr"{ctx['mag']}$^\circ$F"
            offset = ctx["mag"]
    op = "+" if ctx["which"] == "above" else "-"
    comp = ">" if ctx["which"] == "above" else "<"
    which = "above" if ctx["which"] == "above" else "below"
    df = read_sql(
        f"""
      WITH avgs as (
        SELECT sday,
        avg(high) as avg_high,
        stddev(high) as stddev_high,
        avg(low) as avg_low,
        stddev(low) as stddev_low,
        avg((high+low)/2.) as avg_temp,
        stddev((high+low)/2.) as stddev_temp
        from {table} WHERE
        station = %s GROUP by sday)

      SELECT {yr},
      sum(case when o.high {comp}
       (a.avg_high {op} a.stddev_high * {smul} {op} {offset}) then 1 else 0 end
      ) as high_{which},
      sum(case when o.low {comp}
       (a.avg_low {op} a.stddev_low * {smul} {op} {offset}) then 1 else 0 end
      ) as low_{which},
      sum(case when (o.high+o.low)/2. {comp}
       (a.avg_temp {op} a.stddev_temp * {smul} {op} {offset}) then 1 else 0 end
      ) as avg_{which},
      count(*) as days from {table} o, avgs a WHERE o.station = %s
      and o.sday = a.sday and month in %s
      GROUP by yr ORDER by yr ASC
    """,
        pgconn,
        params=(station, station, tuple(months)),
        index_col="yr",
    )
    if df.empty:
        raise NoDataFound("No Data Found.")

    df["high_freq"] = df[f"high_{which}"] / df["days"].astype("f") * 100.0
    df["low_freq"] = df[f"low_{which}"] / df["days"].astype("f") * 100.0
    df["avg_freq"] = df[f"avg_{which}"] / df["days"].astype("f") * 100.0

    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))
    suffix = f"_{which}" if ctx["opt"] == "number" else "_freq"
    avgv = df[varname + suffix].mean()

    colorabove = "r"
    colorbelow = "b"
    if ctx["which"] == "below":
        colorabove, colorbelow = colorbelow, colorabove
    data = df[varname + suffix].values
    bars = ax.bar(
        df.index.values, data, fc=colorabove, ec=colorabove, align="center"
    )
    for i, mybar in enumerate(bars):
        if data[i] < avgv:
            mybar.set_facecolor(colorbelow)
            mybar.set_edgecolor(colorbelow)
    ax.axhline(avgv, lw=2, color="k", zorder=2)
    txt = ax.text(
        bars[10].get_x(),
        avgv,
        "Avg: %.1f%s" % (avgv, "" if ctx["opt"] == "number" else "%"),
        color="yellow",
        fontsize=14,
        va="center",
    )
    txt.set_path_effects([PathEffects.withStroke(linewidth=5, foreground="k")])
    ax.set_ylim(bottom=0)
    ax.set_xlabel("Year")
    ax.set_xlim(bars[0].get_x() - 1, bars[-1].get_x() + 1)
    ax.set_ylabel(
        "Frequency [%]" if ctx["opt"] == "percent" else "Number of Days"
    )
    ax.grid(True)
    title = "\n".join(
        [
            f"[{station}] {nt.sts[station]['name']} "
            f"{df.index.values.min()}-{df.index.values.max()} "
            f"{PDICT4[ctx['opt']]} of Days",
            f"with {PDICT[varname]} {metric} {PDICT3[ctx['which']]} "
            f"Average (month={month.upper()})",
            "Using Period of Record Simple Climatology",
        ]
    )
    fitbox(fig, title, 0.05, 0.95, 0.9, 0.99, ha="center")
    return fig, df


if __name__ == "__main__":
    plotter(dict())
