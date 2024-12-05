"""
This chart presents the crop progress by year.  Since the NASS data is weekly,
a linear interpolation is performed to estimate the daily values.  The chart
presents a yearly trendline as well for a given threshold value.  Due to leap
days, the plotted day of year values are not an exact science.
"""

import calendar

import numpy as np
import pandas as pd
from matplotlib import ticker
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure, get_cmap
from pyiem.reference import state_names
from pyiem.util import get_autoplot_context, utc
from sqlalchemy import text

PDICT = {
    "CPR": "CORN - PROGRESS, MEASURED IN PCT SEEDBED PREPARED",
    "CP": "CORN - PROGRESS, MEASURED IN PCT PLANTED",
    "CE": "CORN - PROGRESS, MEASURED IN PCT EMERGED",
    "CS": "CORN - PROGRESS, MEASURED IN PCT SILKING",
    "CMI": "CORN - PROGRESS, MEASURED IN PCT MILK",
    "CD": "CORN - PROGRESS, MEASURED IN PCT DENTED",
    "CDO": "CORN - PROGRESS, MEASURED IN PCT DOUGH",
    "CMA": "CORN - PROGRESS, MEASURED IN PCT MATURE",
    "CH": "CORN, GRAIN - PROGRESS, MEASURED IN PCT HARVESTED",
    "CSH": "CORN, SILAGE - PROGRESS, MEASURED IN PCT HARVESTED",
    "SPR": "SOYBEANS - PROGRESS, MEASURED IN PCT SEEDBED PREPARED",
    "SP": "SOYBEANS - PROGRESS, MEASURED IN PCT PLANTED",
    "SE": "SOYBEANS - PROGRESS, MEASURED IN PCT EMERGED",
    "SPO": "SOYBEANS - PROGRESS, MEASURED IN PCT FULLY PODDED",
    "SB": "SOYBEANS - PROGRESS, MEASURED IN PCT BLOOMING",
    "SM": "SOYBEANS - PROGRESS, MEASURED IN PCT MATURE",
    "SL": "SOYBEANS - PROGRESS, MEASURED IN PCT DROPPING LEAVES",
    "SS": "SOYBEANS - PROGRESS, MEASURED IN PCT SETTING PODS",
    "SC": "SOYBEANS - PROGRESS, MEASURED IN PCT COLORING",
    "SH": "SOYBEANS - PROGRESS, MEASURED IN PCT HARVESTED",
    "FD": "FIELDWORK - DAYS SUITABLE, MEASURED IN DAYS / WEEK",
}
PDICT2 = {
    "last": "Current value for the most recent week",
    "thres": "Threshold value defined by user",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "nass": True}
    desc["arguments"] = [
        dict(type="state", name="state", default="IA", label="Select State:"),
        dict(
            type="select",
            name="short_desc",
            default="CH",
            options=PDICT,
            label="Which Statistical Category?",
        ),
        {
            "type": "select",
            "name": "w",
            "default": "last",
            "options": PDICT2,
            "label": "Plot trendline for given threshold value",
        },
        {
            "type": "int",
            "name": "threshold",
            "default": 50,
            "label": "Threshold Value [% or days] when set above:",
        },
        dict(type="cmap", name="cmap", default="jet", label="Color Ramp:"),
    ]
    return desc


def plot_trendline(fig, ctx, data, year0, lastyear):
    """Add the right hand side plot of trendline."""
    ax = fig.add_axes([0.55, 0.1, 0.4, 0.8])
    threshold = ctx["threshold"]
    if ctx["w"] == "last":
        threshold = np.max(data[-1, :])
    years = []
    doys = []
    for year in range(year0, lastyear):
        try:
            idx = np.digitize([threshold], data[year - year0, :], right=True)
            years.append(year)
            doys.append(idx[0])
        except ValueError:
            pass

    ax.scatter(years, doys, s=40)
    ax.set_xlim(year0 - 0.5, lastyear + 0.5)
    ax.set_ylim(min(doys) - 5, max(doys) + 5)
    ylabels = []
    yticks = []
    every = [1, 15] if max(doys) - min(doys) > 60 else [1, 8, 15, 22, 29]
    for doy in range(min(doys) - 5, max(doys) + 5):
        ts = pd.Timestamp("2000-01-01") + pd.Timedelta(days=doy)
        if ts.day in every:
            ylabels.append(ts.strftime("%b %d"))
            yticks.append(doy)
    ax.set_yticks(yticks)
    ax.set_yticklabels(ylabels)
    unit = "% Progress" if ctx["short_desc"] != "FD" else " days"
    ax.set_ylabel(f"Date of {threshold:.0f}{unit}")
    ax.grid(True)

    # fit a trendline with a R-squared denoted
    x = np.array(years)
    y = np.array(doys)
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    ax.plot(x, p(x), "r--")
    yhat = p(x)
    ybar = np.sum(y) / len(y)
    ssreg = np.sum((yhat - ybar) ** 2)
    sstot = np.sum((y - ybar) ** 2)
    r2 = ssreg / sstot
    meany = np.mean(doys)
    ax.axhline(meany, lw=2, color="k")
    dt = pd.Timestamp("2000-01-01") + pd.Timedelta(days=int(meany))
    ax.annotate(
        f"Mean: {dt.strftime('%b %d')}",
        xy=(0.9, meany),
        xycoords=("axes fraction", "data"),
        va="top",
    )
    ax.text(
        0.9,
        0.9,
        f"R2={r2:.2f}",
        transform=ax.transAxes,
        ha="center",
    )


def fill100(df: pd.DataFrame) -> pd.DataFrame:
    """Need to account for a NASS quirk."""
    newrows = []
    for year, maxrow in (
        df[["year", "num_value"]].groupby("year").max().iterrows()
    ):
        if maxrow["num_value"] > 99 or year == utc().year:
            continue
        lastrow = df[df["year"] == year].iloc[-1]
        filldate = lastrow["week_ending"] + pd.Timedelta(days=7)
        if filldate.year != year:
            continue
        newrows.append(
            {
                "year": year,
                "week_ending": filldate,
                "num_value": 100,
                "day_of_year": lastrow["day_of_year"] + 7,
            }
        )
    if newrows:
        df = pd.concat([df, pd.DataFrame(newrows)])
    return df.sort_values("week_ending", ascending=True)


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    state = ctx["state"][:2]
    short_desc = PDICT[ctx["short_desc"].upper()]
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            text("""
            select distinct year, week_ending, num_value,
            extract(doy from week_ending)::int as day_of_year
            from nass_quickstats
            where short_desc = :sd and state_alpha = :sa and
            num_value is not null and week_ending is not null
            and extract(year from week_ending) = year
            ORDER by week_ending ASC
        """),
            conn,
            params={"sd": short_desc, "sa": state},
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("ERROR: No data found!")
    if short_desc != "FD":
        # Need to fill out trailing weeks with 100s
        df = fill100(df)
    df["yeari"] = df["year"] - df["year"].min()
    if ctx["short_desc"] == "FD":
        df["num_value"] = df[["num_value", "year"]].groupby("year").cumsum()

    year0 = int(df["year"].min())
    lastyear = int(df["year"].max())
    tt = (
        f"{short_desc} Progress"
        if ctx["short_desc"] != "FD"
        else "Accumulated Days Suitable for Field Work"
    )
    title = (
        f"{state_names[state]} {tt}\n"
        f"USDA NASS {year0:.0f}-{lastyear:.0f} -- "
        "Daily Linear Interpolated Values Between Weekly Reports"
    )
    fig = figure(title=title, apctx=ctx)
    ax = fig.add_axes((0.05, 0.1, 0.35, 0.8))

    data = np.ma.ones((df["yeari"].max() + 1, 366), "f") * -1
    data.mask = np.where(data == -1, True, False)

    lastrow = None
    for _, row in df.iterrows():
        if lastrow is None:
            lastrow = row
            continue

        date = row["week_ending"]
        ldate = lastrow["week_ending"]
        val = int(row["num_value"])
        lval = int(lastrow["num_value"])
        d0 = int(ldate.strftime("%j"))
        d1 = int(date.strftime("%j"))
        if ldate.year == date.year:
            delta = (val - lval) / float(d1 - d0)
            for i, jday in enumerate(range(d0, d1 + 1)):
                data[date.year - year0, jday] = lval + i * delta
        else:
            data[ldate.year - year0, d0:] = np.max(data[ldate.year - year0, :])

        lastrow = row

    plot_trendline(fig, ctx, data, year0, lastyear)

    dlast = np.max(data[-1, :])
    if ctx["w"] == "thres":
        dlast = ctx["threshold"]
    for year in range(year0, lastyear):
        try:
            idx = np.digitize([dlast], data[year - year0, :], right=True)
            ax.text(idx[0], year, "X", va="center", zorder=2, color="white")
        except ValueError:
            pass

    cmap = get_cmap(ctx["cmap"])
    res = ax.imshow(
        data,
        extent=[1, 367, lastyear + 0.5, year0 - 0.5],
        aspect="auto",
        interpolation="none",
        cmap=cmap,
    )
    cax = fig.add_axes((0.42, 0.1, 0.02, 0.8))
    fig.colorbar(res, cax=cax)
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax.set_xticklabels(calendar.month_abbr[1:])
    # We need to compute the domain of this plot
    maxv = np.max(data, 0)
    minv = np.min(data, 0)
    if ctx["short_desc"] == "FD":
        ax.set_xlim(np.argmax(maxv > 0) - 7)
    else:
        ax.set_xlim(
            np.nanargmax(maxv > 0) - 7,
            np.nanargmax(minv >= np.nanmax(minv)) + 7,
        )
    ax.set_ylim(lastyear + 0.5, year0 - 0.5)
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.grid(True)
    unit = "%" if ctx["short_desc"] != "FD" else " days"
    if ctx["w"] == "thres":
        ax.set_xlabel(f"X denotes value of {dlast:.1f}{unit}")
    else:
        lastweek = df["week_ending"].max()
        ax.set_xlabel(
            f"X denotes {lastweek:%d %b %Y} value of {dlast:.1f}{unit}"
        )

    return fig, df
