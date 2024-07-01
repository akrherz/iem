"""
This app generates a heatmap-like presentation of daily climate data
of your choice.  In the case of 'Trailing XX Days', you will want to set
a trailing number of days to evaluate the metric for.
"""

import calendar
import datetime

import matplotlib.colors as mpcolors
import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes, get_cmap
from pyiem.util import get_autoplot_context
from seaborn import heatmap
from sqlalchemy import text

PDICT = {
    "trail_precip_percent": "Trailing XX Days Precip Percent of Average",
    "daily_high_depart": "Daily High Temperature Departure",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    today = datetime.date.today()
    desc["arguments"] = [
        dict(
            type="select",
            options=PDICT,
            default="trail_precip_percent",
            name="var",
            label="Available variables to plot:",
        ),
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select station:",
            network="IACLIMATE",
        ),
        dict(
            type="int",
            name="days",
            default="31",
            label="Trailing Number of Days (when appropriate):",
        ),
        dict(
            type="year",
            default=(today.year - 20),
            label="Start Year of Plot:",
            name="syear",
        ),
        dict(
            type="year",
            default=today.year,
            label="End Year (inclusive) of Plot:",
            name="eyear",
        ),
        dict(type="cmap", name="cmap", default="RdBu", label="Color Ramp:"),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            text("""
            select day, sday, precip, high,
            extract(doy from day)::int as doy,
            year from alldata WHERE station = :station ORDER by day ASC
            """),
            conn,
            params={"station": ctx["station"]},
            index_col="day",
            parse_dates="day",
        )
    if df.empty:
        raise NoDataFound("Did not find any data for station!")
    if ctx["var"] == "trail_precip_percent":
        climo = df[["precip", "sday"]].groupby("sday").mean()
        df["precip_avg"] = df.merge(
            climo, left_on="sday", right_index=True, suffixes=("", "_avg")
        )["precip_avg"]
        df["trail_precip_percent"] = (
            df["precip"].rolling(ctx["days"]).sum()
            / df["precip_avg"].rolling(ctx["days"]).sum()
            * 100.0
        )
        levels = [0, 25, 50, 75, 100, 150, 200, 250, 300]
        label = "Percent"
    else:  # daily_high_depart
        climo = df[["high", "sday"]].groupby("sday").mean()
        df["high_avg"] = df.merge(
            climo, left_on="sday", right_index=True, suffixes=("", "_avg")
        )["high_avg"]
        df["daily_high_depart"] = df["high"] - df["high_avg"]
        levels = list(range(-20, 21, 4))
        label = "Temperature [F] Departure"

    baseyear = max([df["year"].min(), ctx["syear"]])
    endyear = min([df["year"].max(), ctx["eyear"]])
    years = endyear - baseyear + 1
    if years < 1:
        raise NoDataFound("Station data does not exist for the period picked.")
    cmap = get_cmap(ctx["cmap"])
    norm = mpcolors.BoundaryNorm(levels, cmap.N)
    data = np.full((years, 366), np.nan)
    df2 = df[(df["year"] >= baseyear) & (df["year"] <= endyear)]
    for day, row in df2.iterrows():
        data[day.year - baseyear, row["doy"] - 1] = row[ctx["var"]]

    title = (
        f"{ctx['_sname']} ({ctx['syear']}-{ctx['eyear']})\n"
        f"{PDICT[ctx['var']].replace('XX', str(ctx['days']))}"
    )
    fig, ax = figure_axes(title=title, apctx=ctx)
    heatmap(
        data,
        cmap=cmap,
        norm=norm,
        ax=ax,
        cbar_kws={"spacing": "proportional", "label": label},
    )
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax.set_xticklabels(calendar.month_abbr[1:], rotation=0)
    yticks = []
    yticklabels = []
    delta = 5 if (endyear - baseyear) < 30 else 10
    for i, year in enumerate(range(baseyear, endyear + 1)):
        if year % delta == 0:
            yticks.append(i + 0.5)
            yticklabels.append(year)
    ax.set_yticks(yticks[::-1])
    ax.set_yticklabels(yticklabels[::-1], rotation=0)
    ax.xaxis.grid(True, color="k")
    return fig, df
