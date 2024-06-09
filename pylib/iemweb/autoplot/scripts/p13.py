"""
This chart presents the start or end date of the
warmest 91 day period each year.
"""

import datetime

import matplotlib.colors as mpcolors
import numpy as np
import pandas as pd
from matplotlib import cm
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import centered_bins, figure_axes, get_cmap
from pyiem.util import get_autoplot_context
from scipy import stats
from sqlalchemy import text

PDICT = {"end_summer": "End of Summer", "start_summer": "Start of Summer"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select Station:",
            network="IACLIMATE",
        ),
        dict(
            type="select",
            name="which",
            default="end_summer",
            label="Which value to plot:",
            options=PDICT,
        ),
        {
            "type": "cmap",
            "name": "cmap",
            "default": "RdYlGn",
            "label": "Color Ramp:",
        },
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    which = ctx["which"]
    station = ctx["station"]

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            text(
                """
            with obs as (
                select day, year, avg((high+low)/2.) OVER
                (ORDER by day ASC rows 91 preceding) from alldata
                where station = :sid and day > '1893-01-01'
            ), agg as (
                select day, year, avg,
                rank() OVER (PARTITION by year ORDER by avg DESC, day DESC)
                from obs
            )
            select year, extract(doy from day)::int as doy, avg from agg
            where rank = 1 ORDER by year ASC
        """
            ),
            conn,
            params={"sid": station},
            index_col="year",
        )
    if df.empty:
        raise NoDataFound("No Data Found.")
    today = datetime.date.today()
    df["departure"] = df["avg"] - df["avg"].mean()
    df["plot_doy"] = df["doy"] - (0 if which == "end_summer" else 91)
    if today.year in df.index and df.at[today.year, "doy"] < 270:
        df = df.drop(today.year)

    t1 = "End" if which == "end_summer" else "Start"
    title = (
        f"{ctx['_sname']} :: {PDICT.get(which)}\n"
        f"{t1} Date of Warmest (Avg Temp) 91 Day Period"
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)

    cmap = get_cmap(ctx["cmap"])
    bins = centered_bins(df["departure"].abs().max())
    norm = mpcolors.BoundaryNorm(bins, cmap.N)
    ax.scatter(df.index, df["plot_doy"], c=cmap(norm(df["departure"].values)))
    ax.grid(True)
    ax.set_ylabel(f"{t1} Date")

    sm = cm.ScalarMappable(norm, cmap)
    sm.set_array(bins)
    cb = fig.colorbar(sm, extend="neither", ax=ax)
    cb.set_label(r"Summer Avg Temperature Departure $^\circ$F")

    yticks = []
    yticklabels = []
    for i in np.arange(df["plot_doy"].min() - 5, df["plot_doy"].max() + 5, 1):
        ts = datetime.datetime(2000, 1, 1) + datetime.timedelta(days=int(i))
        if ts.day in [1, 8, 15, 22, 29]:
            yticks.append(i)
            yticklabels.append(ts.strftime("%-d %b"))
    ax.set_yticks(yticks)
    ax.set_yticklabels(yticklabels)

    h_slope, intercept, r_value, _, _ = stats.linregress(
        df.index.values, df["plot_doy"].values
    )
    ax.plot(
        df.index.values, h_slope * df.index.values + intercept, lw=2, color="r"
    )

    avgd = datetime.datetime(2000, 1, 1) + datetime.timedelta(
        days=int(df["plot_doy"].mean())
    )
    ax.text(
        0.1,
        0.03,
        (
            f"Avg Date: {avgd:%-d %b}, "
            f"slope: {h_slope * 100.:.2f} days/century, "
            f"R$^2$={r_value**2:.2f}"
        ),
        transform=ax.transAxes,
        va="bottom",
    )
    ax.set_xlim(df.index.values[0] - 1, df.index.values[-1] + 1)
    ax.set_ylim(df["plot_doy"].min() - 5, df["plot_doy"].max() + 5)

    return fig, df
