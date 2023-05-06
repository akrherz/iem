"""
This chart presents the crop progress by year.
The most recent value for the current year is denoted on each of the
previous years on record.

<p><strong>Updated 15 June 2021</strong>: The options for this autoplot
were changed and not backwards compatable with previous URIs, sorry.</p>
"""
import calendar

import numpy as np
import pandas as pd
from matplotlib import ticker
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes, get_cmap
from pyiem.reference import state_names
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn

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
        dict(type="cmap", name="cmap", default="jet", label="Color Ramp:"),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    state = ctx["state"][:2]
    short_desc = PDICT[ctx["short_desc"].upper()]
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            """
            select distinct year, week_ending, num_value,
            extract(doy from week_ending)::int as day_of_year
            from nass_quickstats
            where short_desc = %s and state_alpha = %s and
            num_value is not null and week_ending is not null
            ORDER by week_ending ASC
        """,
            conn,
            params=(short_desc, state),
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("ERROR: No data found!")
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
    (fig, ax) = figure_axes(title=title, apctx=ctx)

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

    dlast = np.max(data[-1, :])
    for year in range(year0, lastyear):
        idx = np.digitize([dlast], data[year - year0, :], right=True)
        ax.text(idx[0], year, "X", va="center", zorder=2, color="white")

    cmap = get_cmap(ctx["cmap"])
    res = ax.imshow(
        data,
        extent=[1, 367, lastyear + 0.5, year0 - 0.5],
        aspect="auto",
        interpolation="none",
        cmap=cmap,
    )
    fig.colorbar(res)
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax.set_xticklabels(calendar.month_abbr[1:])
    # We need to compute the domain of this plot
    maxv = np.max(data, 0)
    minv = np.min(data, 0)
    if ctx["short_desc"] == "FD":
        ax.set_xlim(np.argmax(maxv > 0) - 7)
    else:
        ax.set_xlim(np.argmax(maxv > 0) - 7, np.argmax(minv > 99) + 7)
    ax.set_ylim(lastyear + 0.5, year0 - 0.5)
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.grid(True)
    lastweek = df["week_ending"].max()
    unit = "%" if ctx["short_desc"] != "FD" else " days"
    ax.set_xlabel(f"X denotes {lastweek:%d %b %Y} value of {dlast:.1f}{unit}")

    return fig, df


if __name__ == "__main__":
    plotter({"short_desc": "FD"})
