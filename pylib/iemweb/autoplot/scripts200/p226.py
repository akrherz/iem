"""
This plot is not meant for interactive use, but a backend for
CWA plots.
"""

from datetime import UTC, datetime, timedelta
from typing import Annotated

import geopandas as gpd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot.geoplot import MapPlot
from pyiem.reference import Z_OVERLAY2

from iemweb.autoplot.description import (
    DateTimeArg,
    IntArg,
    NetworkSelectArg,
    PlotDescription,
)
from iemweb.autoplot.params import AutoplotParams


class Params(AutoplotParams):
    """Request parameters."""

    cwsu: Annotated[
        str, NetworkSelectArg(network="CWSU", label="Select CWSU:")
    ] = "ZMA"
    num: Annotated[int, IntArg(label="CWA Number:")] = 207
    issue: Annotated[
        datetime,
        DateTimeArg(
            label="UTC Timestamp of the CWA Issuance "
            "(or will search backwards < 1 day):",
            min="2015/12/31 0000",
            default="2023/02/03 1653",
        ),
    ]


def get_description() -> PlotDescription:
    """Return a description of how to call this plotter."""
    return PlotDescription.from_model(
        Params,
        description=__doc__ or "",
        cache=3600,
        data=True,
        defaults={"_r": "t"},
    )


def plotter(ctx: Params):
    """Go"""
    num = ctx.num

    with get_sqlalchemy_conn("postgis") as conn:
        df = gpd.read_postgis(
            sql_helper("""
    select geom, expire at time zone 'UTC' as expire,
    issue at time zone 'UTC' as issue, narrative from cwas
    where center = :center and num = :num and
    issue > :sts and issue <= :ets ORDER by issue DESC LIMIT 1"""),
            conn,
            params={
                "center": ctx.cwsu,
                "num": num,
                "sts": ctx.issue - timedelta(hours=24),
                "ets": ctx.issue,
            },
            index_col=None,
            geom_col="geom",
        )  # type: ignore
    if df.empty:
        raise NoDataFound("CWA Event was not found, sorry.")
    for col in ["issue", "expire"]:
        df[col] = df[col].dt.tz_localize(UTC)
    bounds = df["geom"].total_bounds
    row = df.iloc[0]
    mp = MapPlot(
        apctx=ctx,
        title=(
            f"{ctx.cwsu} Center Weather Advisory (CWA) #{ctx.num} "
            f"till {row['expire']:%Y-%m-%d %H:%M} UTC"
        ),
        subtitle=row["narrative"],
        sector="spherical_mercator",
        west=bounds[0] - 1.2,
        south=bounds[1] - 1.2,
        east=bounds[2] + 1.2,
        north=bounds[3] + 1.2,
        nocaption=True,
    )
    df.to_crs(mp.panels[0].crs).plot(
        ax=mp.panels[0].ax,
        aspect=None,
        facecolor="None",
        edgecolor="k",
        linewidth=4,
        zorder=Z_OVERLAY2,
    )
    mp.drawcounties()
    radtime = mp.overlay_nexrad(
        df["issue"].iloc[0].to_pydatetime(),
        product="N0Q",
        caxpos=[-0.6, 0.05, 0.35, 0.04],  # TODO make this appear nicer
    )
    if radtime is not None:
        mp.fig.text(
            0.65,
            0.02,
            f"RADAR Valid: {radtime:%Y-%m-%d %H:%M} UTC",
            ha="center",
        )

    return mp.fig, df.drop(["geom", "issue", "expire"], axis=1)
