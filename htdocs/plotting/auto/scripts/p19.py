"""histogram"""
import datetime

import numpy as np
import pandas as pd
from matplotlib.font_manager import FontProperties
from sqlalchemy import text
from pyiem.plot import figure, get_cmap
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound

MDICT = {
    "all": "No Month/Time Limit",
    "spring": "Spring (MAM)",
    "fall": "Fall (SON)",
    "winter": "Winter (DJF)",
    "summer": "Summer (JJA)",
    "jan": "January",
    "feb": "February",
    "mar": "March",
    "apr": "April",
    "may": "May",
    "jun": "June",
    "jul": "July",
    "aug": "August",
    "sep": "September",
    "oct": "October",
    "nov": "November",
    "dec": "December",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc[
        "description"
    ] = """This chart displays a histogram of daily high
    and low temperatures for a station of your choice. If you optionally
    choose to overlay a given year's data and select winter, the year of
    the December is used for the plot. For example, the winter of 2017 is
    Dec 2017 thru Feb 2018.  The plot details the temperature bin with the
    highest frequency."""
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATAME",
            label="Select Station:",
            network="IACLIMATE",
        ),
        dict(
            type="int",
            name="binsize",
            default="10",
            label="Histogram Bin Size:",
        ),
        dict(
            type="select",
            name="month",
            default="all",
            label="Month Limiter",
            options=MDICT,
        ),
        dict(
            type="year",
            optional=True,
            default=datetime.date.today().year,
            label="Optional: Overlay Observations for given year",
            name="year",
        ),
        dict(type="cmap", name="cmap", default="Blues", label="Color Ramp:"),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    binsize = ctx["binsize"]
    month = ctx["month"]
    year = ctx.get("year")
    if month == "all":
        months = range(1, 13)
    elif month == "fall":
        months = [9, 10, 11]
    elif month == "winter":
        months = [12, 1, 2]
    elif month == "spring":
        months = [3, 4, 5]
    elif month == "summer":
        months = [6, 7, 8]
    else:
        ts = datetime.datetime.strptime(f"2000-{month}-01", "%Y-%b-%d")
        # make sure it is length two for the trick below in SQL
        months = [ts.month, 999]
    with get_sqlalchemy_conn("coop") as conn:
        ddf = pd.read_sql(
            text(
                "SELECT high, low, year, month from alldata "
                "WHERE station = :station "
                "and year > 1892 and high >= low and month in :months "
            ),
            conn,
            params={"station": station, "months": tuple(months)},
            index_col=None,
        )
    if ddf.empty:
        raise NoDataFound("No Data Found.")
    ddf["range"] = ddf["high"] - ddf["low"]
    xbins = np.arange(ddf["low"].min() - 3, ddf["low"].max() + 3, binsize)
    ybins = np.arange(ddf["high"].min() - 3, ddf["high"].max() + 3, binsize)

    hist, xedges, yedges = np.histogram2d(
        ddf["low"], ddf["high"], [xbins, ybins]
    )
    rows = []
    for i, xedge in enumerate(xedges[:-1]):
        for j, yedge in enumerate(yedges[:-1]):
            rows.append(dict(high=yedge, low=xedge, count=hist[i, j]))
    df = pd.DataFrame(rows)
    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    years = float(datetime.datetime.now().year - ab.year)
    hist = np.ma.array(hist / years)
    hist.mask = np.where(hist < (1.0 / years), True, False)
    ar = np.argwhere(hist.max() == hist)

    subtitle = (
        "Daily High vs Low Temperature Histogram + Range between Low + High "
        f"(month={month.upper()})"
    )
    title = (
        f"{ctx['_sname']} ({ddf['year'].min():.0f}-{ddf['year'].max():.0f})"
    )
    fig = figure(title=title, subtitle=subtitle, apctx=ctx)
    kax = fig.add_axes([0.65, 0.5, 0.3, 0.36])
    kax.grid(True)
    kax.text(
        0.02,
        1.02,
        "Daily Temperature Range Histogram + CDF",
        transform=kax.transAxes,
        bbox=dict(color="tan"),
        va="bottom",
    )
    kax.hist(ddf["range"].values, density=True, color="lightgreen")
    kax.set_ylabel("Density")
    kax2 = kax.twinx()
    kax2.set_ylabel("Cumulative Density")
    kax2.hist(
        ddf["range"].values,
        density=True,
        cumulative=100,
        histtype="step",
        color="k",
    )
    kax.set_xlim((kax.get_xlim()[0], ddf["range"].max()))

    # Table of Percentiles
    ranks = ddf["range"].quantile(np.arange(0, 1.0001, 0.0025))
    xpos = 0.62
    ypos = 0.37
    fig.text(
        0.65,
        ypos + 0.03,
        "Daily Temperature Range Percentiles",
        bbox=dict(color="tan"),
    )
    fig.text(xpos - 0.01, ypos - 0.01, "Percentile   Value")
    ypos -= 0.01
    monofont = FontProperties(family="monospace")
    for (q, val) in ranks.items():
        if 0.02 < q < 0.98 and (q * 100.0 % 10) != 0:
            continue
        if q > 0.1 and int(q * 100) in [20, 90]:
            xpos += 0.13
            ypos = 0.37
            fig.text(xpos - 0.01, ypos - 0.01, "Percentile   Value")
            ypos -= 0.01
        ypos -= 0.025
        label = f"{q * 100:-6g} {val:-6.0f}"
        fig.text(xpos, ypos, label, fontproperties=monofont)

    ax = fig.add_axes([0.07, 0.17, 0.5, 0.73])
    res = ax.pcolormesh(xedges, yedges, hist.T, cmap=get_cmap(ctx["cmap"]))
    cax = fig.add_axes([0.07, 0.08, 0.5, 0.01])
    fig.colorbar(res, label="Days per Year", orientation="horizontal", cax=cax)
    ax.grid(True)
    ax.set_ylabel(r"High Temperature $^{\circ}\mathrm{F}$")
    ax.set_xlabel(r"Low Temperature $^{\circ}\mathrm{F}$")

    xmax = ar[0][0]
    ymax = ar[0][1]
    ax.text(
        0.65,
        0.15,
        (
            f"Largest Frequency: {hist[xmax, ymax]:.1f} days\n"
            f"High: {yedges[ymax]:.0f}-{yedges[ymax + 1]:.0f} "
            f"Low: {xedges[xmax]:.0f}-{xedges[xmax + 1]:.0f}"
        ),
        ha="center",
        va="center",
        transform=ax.transAxes,
        bbox=dict(color="white"),
    )
    if ddf["high"].min() < 32:
        ax.axhline(32, linestyle="-", lw=1, color="k")
    ax.text(
        ax.get_xlim()[1],
        32,
        r"32$^\circ$F",
        va="center",
        ha="right",
        color="white",
        bbox=dict(color="k"),
        fontsize=8,
    )
    if ddf["low"].min() < 32:
        ax.axvline(32, linestyle="-", lw=1, color="k")
    ax.text(
        32,
        ax.get_ylim()[1],
        r"32$^\circ$F",
        va="top",
        ha="center",
        color="white",
        bbox=dict(facecolor="k", edgecolor="none"),
        fontsize=8,
    )
    if year:
        label = str(year)
        if month == "winter":
            ddf["year"] = (
                ddf[((ddf["month"] == 1) | (ddf["month"] == 2))]["year"] - 1
            )
            label = f"Dec {year} - Feb {year + 1}"
        ddf2 = ddf[ddf["year"] == year]
        ax.scatter(
            ddf2["low"],
            ddf2["high"],
            marker="o",
            s=30,
            label=label,
            edgecolor="yellow",
            facecolor="red",
        )
        ax.legend()

    return fig, df


if __name__ == "__main__":
    plotter({})
