"""
This tool generates a diagnostic plot of how a given NWS UGC geometry has
changed over time.  The NWS updates their UGC databases about every year and
some IEM processing attempts to keep track of all this.  This is not an easy
nor exact science.
"""

from typing import Annotated

import geopandas as gpd
from matplotlib.patches import Rectangle
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import MapPlot, get_cmap
from pyiem.reference import Z_OVERLAY2

from iemweb.autoplot.description import (
    CmapArg,
    PlotDescription,
    SelectArg,
    UgcArg,
)
from iemweb.autoplot.params import AutoplotParams

PDICT = {
    "yes": "Show the Fire Weather variant",
    "no": "Do not show the Fire Weather variant",
}


class Params(AutoplotParams):
    """Request parameters."""

    ugc: Annotated[str, UgcArg(label="Select the UGC:")] = "IAC169"
    cmap: Annotated[str, CmapArg(label="Select a colormap")] = "viridis"
    fire: Annotated[
        str, SelectArg(options=PDICT, label="Show the Fire Weather variant?")
    ] = "no"


def get_description() -> PlotDescription:
    """Return a description of how to call this plotter."""
    return PlotDescription.from_model(
        Params, description=__doc__ or "", data=True
    )


def plotter(ctx: Params):
    """Go"""
    sourceop = "=" if ctx.fire == "yes" else "!="
    with get_sqlalchemy_conn("postgis") as pgconn:
        ugcdf = gpd.read_postgis(
            sql_helper(
                """
    select * from ugcs where ugc = :ugc and source {sourceop} 'fz'
    ORDER by begin_ts ASC
                       """,
                sourceop=sourceop,
            ),
            pgconn,
            params={"ugc": ctx.ugc},
            parse_dates=["begin_ts", "end_ts"],
            geom_col="geom",
        )  # type: ignore
    if ugcdf.empty:
        raise NoDataFound("No UGC data found.")

    ugcdf["begin_ts"] = ugcdf["begin_ts"].dt.strftime("%Y-%m-%d")
    ugcdf["end_ts"] = ugcdf["end_ts"].dt.strftime("%Y-%m-%d")
    ugcdf["label"] = (
        ugcdf["begin_ts"]
        + " to "
        + ugcdf["end_ts"].fillna("Now")
        + " ["
        + ugcdf["wfo"]
        + "]"
    )
    cmap = get_cmap(ctx.cmap)
    if len(ugcdf) == 1:
        ugcdf["color"] = [cmap(0.5)]
    else:
        ugcdf["color"] = cmap(
            (ugcdf.index - ugcdf.index.min())
            / (ugcdf.index.max() - ugcdf.index.min())
        ).tolist()
    bnds = ugcdf.total_bounds
    dx = bnds[2] - bnds[0]
    dy = bnds[3] - bnds[1]
    buffer = max(dx, dy) * 0.1
    fxextra = ", Fire Weather variant shown" if ctx.fire == "yes" else ""
    mp = MapPlot(
        apctx=ctx,
        sector="spherical_mercator",
        west=bnds[0] + dx * 0.2 - buffer,
        south=bnds[1] - buffer,
        east=bnds[2] - dx * 0.2 + buffer,
        north=bnds[3] + buffer,
        title=f"UGC {ctx.ugc} '{ugcdf.loc[0]['name']}'",
        subtitle=f"Found {len(ugcdf)} changes{fxextra}",
        axes_position=(0.02, 0.04, 0.62, 0.83),
        nocaption=True,
        nostates=True,
        background="World_Topo_Map",
    )

    ugcdf.to_crs(mp.panels[0].crs).plot(
        ax=mp.panels[0].ax,
        aspect=None,
        facecolor="None",
        edgecolor=ugcdf["color"],
        lw=2.5,
        zorder=Z_OVERLAY2,
    )

    handles = []
    for _i, row in ugcdf.iterrows():
        handles.append(
            Rectangle(
                (0, 0),
                1,
                1,
                fc="None",
                edgecolor=row["color"],
            )
        )

    legend = mp.panels[0].ax.legend(
        handles,
        ugcdf["label"].to_list(),  # type: ignore
        loc="upper left",
        fontsize=10,
        framealpha=1,
        bbox_to_anchor=(1.0, 0.95),
    )
    # update the legend z-index
    legend.set_zorder(Z_OVERLAY2)

    return mp.fig, ugcdf.drop(columns="geom")
