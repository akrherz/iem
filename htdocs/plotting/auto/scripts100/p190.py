"""
This chart presents the year that the present day climatology record resides.
"""
import calendar

import matplotlib.colors as mpcolors
import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure, get_cmap
from pyiem.util import get_autoplot_context


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
        dict(type="cmap", name="cmap", default="jet", label="Color Ramp:"),
    ]
    return desc


def magic(fig, ax, df, colname, title, ctx):
    """You can do magic"""
    df2 = df[df[colname] == 1]

    ax.text(0, 1.02, title, transform=ax.transAxes)
    ax.set_xlim(0, 367)
    ax.grid(True)
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax.set_xticklabels(calendar.month_abbr[1:], rotation=45)

    bbox = ax.get_position()
    sideax = fig.add_axes([bbox.x1 + 0.002, bbox.y0, 0.04, 0.35])
    ylim = [df["year"].min() - 1, df["year"].max() + 1]
    year0 = ylim[0] - (ylim[0] % 10)
    year1 = ylim[1] + (10 - ylim[1] % 10)
    cmap = get_cmap(ctx["cmap"])
    norm = mpcolors.BoundaryNorm(np.arange(year0, year1 + 1, 10), cmap.N)
    ax.scatter(df2["doy"], df2["year"], color=cmap(norm(df2["year"].values)))
    ax.set_yticks(np.arange(year0, year1, 20))
    if colname.find("_high_") == -1:
        ax.set_yticklabels([])
    ax.set_ylim(year0, year1)
    cnts, edges = np.histogram(
        df2["year"].values, np.arange(year0, year1 + 1, 10)
    )
    sideax.barh(
        edges[:-1], cnts, height=10, align="edge", color=cmap(norm(edges[:-1]))
    )
    sideax.set_yticks(np.arange(year0, year1, 20))
    sideax.set_yticklabels([])
    sideax.set_ylim(year0, year1)
    sideax.grid(True)
    sideax.set_xlabel("Decade\nCount")


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            """
        WITH data as (
            SELECT sday, day, year,
            rank() OVER (PARTITION by sday ORDER by high DESC NULLS LAST)
                as max_high_rank,
            rank() OVER (PARTITION by sday ORDER by high ASC NULLS LAST)
                as min_high_rank,
            rank() OVER (PARTITION by sday ORDER by low DESC NULLS LAST)
                as max_low_rank,
            rank() OVER (PARTITION by sday ORDER by low ASC NULLS LAST)
                as min_low_rank,
            rank() OVER (PARTITION by sday ORDER by precip DESC NULLS LAST)
                as max_precip_rank
            from alldata WHERE station = %s)
        SELECT *,
        extract(doy from
        ('2000-'||substr(sday, 1, 2)||'-'||substr(sday, 3, 2))::date) as doy
        from data WHERE max_high_rank = 1 or min_high_rank = 1 or
        max_low_rank = 1 or min_low_rank = 1 or max_precip_rank = 1
        ORDER by day ASC
        """,
            conn,
            params=(station,),
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No Data Found.")

    title = f"{ctx['_sname']} Year of Daily Records, ties included"
    fig = figure(apctx=ctx, title=title)
    axwidth = 0.265
    x0 = 0.04
    ax = fig.add_axes([x0, 0.54, axwidth, 0.35])
    magic(fig, ax, df, "max_high_rank", "Maximum High (warm)", ctx)
    ax = fig.add_axes([x0, 0.09, axwidth, 0.35])
    magic(fig, ax, df, "min_high_rank", "Minimum High (cold)", ctx)
    ax = fig.add_axes([x0 + 0.32, 0.54, axwidth, 0.35])
    magic(fig, ax, df, "max_low_rank", "Maximum Low (warm)", ctx)
    ax = fig.add_axes([x0 + 0.32, 0.09, axwidth, 0.35])
    magic(fig, ax, df, "min_low_rank", "Minimum Low (cold)", ctx)
    ax = fig.add_axes([x0 + 0.64, 0.09, axwidth, 0.35])
    magic(fig, ax, df, "max_precip_rank", "Maximum Precipitation", ctx)

    return fig, df


if __name__ == "__main__":
    plotter({})
