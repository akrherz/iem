"""
This data is courtesy of <a href="{LL}">Vaisala NLDN</a>.  The IEM
processes a data stream by NLDN to construct this heatmap. The stroke
density is computed over a two by two kilometer grid constructed using
a US National Atlas Albers (EPSG:9311) projection.  You are limited to plot
less than 32 days worth of data at a time.</p>

<p><strong>Note:</strong> Due to some lame reasons, it is difficult to
document what data gaps exist within this dataset.  In general, the
coverage should be good outside of the major gap on 10 August 2020 due
to the derecho power outage.</p>
"""

import datetime
from zoneinfo import ZoneInfo

import geopandas as gpd
import matplotlib.colors as mpcolors
import numpy as np
from pyiem.exceptions import NoDataFound
from pyiem.plot import MapPlot, get_cmap, pretty_bins
from pyiem.reference import EPSG, Z_CLIP2, state_bounds
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn, utc

LL = (
    "https://www.vaisala.com/en/products/"
    "national-lightning-detection-network-nldn"
)


def get_description():
    """Return a dict describing how to call this plotter"""
    t24 = utc() - datetime.timedelta(hours=24)
    return {
        "data": False,
        "description": __doc__.replace("{LL}", LL),
        "gallery": {
            "sts": "2024-05-21 1600",
            "ets": "2024-05-21 2300",
        },
        "arguments": [
            dict(
                type="state",
                name="state",
                default="IA",
                label="Select CONUS-Only State:",
            ),
            dict(
                type="datetime",
                default=f"{t24:%Y/%m/%d %H%M}",
                name="sts",
                label="Start Timestamp (UTC):",
                min="2016/10/12 0000",
            ),
            dict(
                type="datetime",
                default=f"{utc():%Y/%m/%d %H%M}",
                name="ets",
                label="End Timestamp (UTC):",
                min="2016/10/12 0000",
            ),
            dict(
                type="cmap",
                name="cmap",
                default="inferno",
                label="Color Ramp:",
            ),
        ],
    }


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    state = ctx["state"]
    sts = ctx["sts"].replace(tzinfo=ZoneInfo("UTC"))
    ets = ctx["ets"].replace(tzinfo=ZoneInfo("UTC"))
    if (ets - sts).total_seconds() >= (32 * 86400):
        raise NoDataFound("Must pick period less than 32 days long")

    bnds = state_bounds[state]
    with get_sqlalchemy_conn("nldn") as conn:
        giswkt = f"LINESTRING({bnds[0]} {bnds[1]}, {bnds[2]} {bnds[3]})"
        df = gpd.read_postgis(
            """
            SELECT ST_Transform(geom, 9311) as geo
            from nldn_all WHERE valid >= %s and valid < %s and
            ST_Contains(
                ST_SetSRID(ST_Envelope(%s::geometry),
                4326), geom)
            """,
            conn,
            params=(sts, ets, giswkt),
            geom_col="geo",
        )
    with get_sqlalchemy_conn("postgis") as conn:
        statedf = gpd.read_postgis(
            "SELECT st_transform(the_geom, 9311) as geo from states "
            "WHERE state_abbr = %s",
            conn,
            params=(state,),
            geom_col="geo",
        )
    if not df.empty:
        df = gpd.sjoin(df, statedf, predicate="within")
    [xmin, ymin, xmax, ymax] = statedf.total_bounds
    buffer = 30_000
    title = (
        f"{sts:%-d %b %Y %H%M}Z - {ets:%-d %b %Y %H%M}Z :: "
        f"{len(df.index):,.0f} Lightning Strokes"
    )
    mp = MapPlot(
        state=state,
        title=title,
        subtitle=(
            "Data courtesy of National Lightning Detection Network by Vaisala,"
            " processed by IEM"
        ),
        west=xmin - buffer,
        east=xmax + buffer,
        south=ymin - buffer,
        north=ymax + buffer,
        projection=EPSG[2163],
        continentalcolor="white",
    )
    if not df.empty:
        xaxis = np.arange(xmin, xmax, 2000.0)
        yaxis = np.arange(ymin, ymax, 2000.0)
        H, xedges, yedges = np.histogram2d(
            df["geo"].x,
            df["geo"].y,
            bins=(xaxis, yaxis),
        )
        H = H.transpose()
        bins = pretty_bins(0, np.max(H))
        if bins[1] > 1:
            bins[0] = 1
        cmap = get_cmap(ctx["cmap"])
        cmap.set_under("white")
        norm = mpcolors.BoundaryNorm(bins, cmap.N)
        xx, yy = np.meshgrid(xedges, yedges)
        mp.panels[0].pcolormesh(
            xx,
            yy,
            np.where(H > 0, H, np.nan),
            norm=norm,
            cmap=cmap,
            zorder=Z_CLIP2,
            crs=EPSG[2163],
        )
        mp.draw_colorbar(bins, cmap, norm, title="strokes per 2x2 km cell")
    else:
        mp.fig.text(0.5, 0.5, "No Strokes Found in Domain.", ha="center")
    mp.draw_mask("state")
    mp.drawcounties()

    return mp.fig, None
