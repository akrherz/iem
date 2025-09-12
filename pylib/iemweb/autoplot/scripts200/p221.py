"""
The NCEP deterministic HRRR model forecast produces a post
processed field that is meant to resemble RADAR reflectivity.  The
lowest 1km HRRR product is plotted along with the IEM mosaic NWS
NEXRAD base reflectivity.

<p><strong>Caution:</strong> This autoplot is very slow to generate,
please be patient!
"""

from datetime import datetime, timedelta, timezone
from functools import partial
from io import BytesIO
from multiprocessing import Pool

import matplotlib.colors as mpcolors
import numpy as np
import pygrib
import pyproj
from affine import Affine
from PIL import Image
from pyiem.plot import MapPlot, ramp2df
from pyiem.util import LOG, archive_fetch, utc

PDICT = {
    "sector": "Plot by State / Sector",
    "cwa": "Plot by NWS CWA / WFO",
}
FONTSIZE = 32


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"data": False, "description": __doc__}
    # Lame default to cut down on CI time :/
    sts = utc() + timedelta(hours=10)
    desc["arguments"] = [
        dict(
            type="select",
            name="w",
            default="sector",
            options=PDICT,
            label="Plot for which domain type",
        ),
        dict(
            type="csector",
            name="sector",
            default="IA",
            label="Select state/sector",
        ),
        dict(
            type="networkselect",
            name="cwa",
            default="DMX",
            label="Select WFO / CWA:",
            network="WFO",
        ),
        dict(
            type="datetime",
            name="valid",
            default=sts.strftime("%Y/%m/%d %H00"),
            max=sts.strftime("%Y/%m/%d %H00"),
            label="Plot Valid At (UTC Timestamp):",
            min="2014/01/01 0000",
        ),
    ]
    return desc


def mp_factory(ctx):
    """Make"""
    if ctx["w"] == "sector":
        sector = "state" if len(ctx["sector"]) == 2 else ctx["sector"]
        state = ctx["sector"]
        cwa = ""
    else:
        sector = "cwa"
        state = ""
        cwa = ctx["cwa"]
    return MapPlot(
        apctx=ctx,
        sector=sector,
        nologo=True,
        state=state,
        cwa=cwa,
        nocaption=True,
    )


def forecast2image(
    ctx: dict, valid: datetime, fhour: int
) -> list[int, bytes | None]:
    """Overlay things."""
    ts = valid - timedelta(hours=fhour)
    if ts >= utc():
        return fhour, None
    ppath = ts.strftime("%Y/%m/%d/model/hrrr/%H/hrrr.t%Hz.refd.grib2")
    with archive_fetch(ppath) as gribfn:
        if gribfn is None:
            return fhour, None
        try:
            with pygrib.open(gribfn) as grbs:
                grb = grbs.select(
                    shortName="refd", level=1000, forecastTime=fhour * 60
                )[0]
                pparams = grb.projparams
                lat1 = grb["latitudeOfFirstGridPointInDegrees"]
                lon1 = grb["longitudeOfFirstGridPointInDegrees"]
                llx, lly = pyproj.Proj(pparams)(lon1, lat1)
                # The reprojected first grid cell is the centroid
                # not the outer edge
                aff = Affine(
                    grb["DxInMetres"],
                    0.0,
                    llx - grb["DxInMetres"] / 2.0,
                    0.0,
                    -grb["DyInMetres"],
                    lly
                    + grb["DyInMetres"] * grb["Ny"]
                    + grb["DyInMetres"] / 2.0,
                )

                ref = grb["values"]
        except Exception as exp:
            LOG.exception(exp)
            return fhour, None
    ref = np.where(ref < -9, -100, ref)
    # HRRR anything below -9 is missing
    mp = mp_factory(ctx)
    mp.fig.text(
        0.1,
        0.92,
        f"HRRR Init:{ts:%d/%H} Forecast Hour:{fhour}",
        fontsize=FONTSIZE,
    )
    mp.imshow(
        ref,
        affine=aff,
        crs=pparams,
        clevs=range(-30, 96, 4),
        cmap=ctx["cmap"],
        clip_on=False,
        clevstride=5,
    )
    if ctx["w"] != "sector" and ctx["sector"] != "conus":
        mp.drawcounties()
    buf = BytesIO()
    mp.fig.savefig(buf, format="png")
    mp.close()
    return fhour, buf.getvalue()


def add_obs(img, ctx, valid):
    """Plot the validation."""
    mp = mp_factory(ctx)
    mp.fig.text(
        0.05,
        0.92,
        f"NEXRAD MOSAIC {valid:%Y-%m-%d %H:%M} UTC",
        fontsize=FONTSIZE,
        bbox=dict(color="white"),
    )
    mp.overlay_nexrad(valid)
    if ctx["w"] != "sector" and ctx["sector"] != "conus":
        mp.drawcounties()
    buf = BytesIO()
    mp.fig.savefig(buf, format="png")
    buf.seek(0)
    with Image.open(buf).resize((512, 386)) as tmp:
        img.paste(tmp, (0, 0))
    buf.close()
    mp.close()


def plotter(ctx: dict):
    """Go"""
    valid = ctx["valid"].replace(tzinfo=timezone.utc)
    ramp = ramp2df("composite_n0q")
    ctx["cmap"] = mpcolors.ListedColormap(
        ramp[["r", "g", "b"]].to_numpy() / 256,
    )
    ctx["cmap"].set_under((0, 0, 0, 0))

    width = 512
    height = 386
    img = Image.new("RGB", (width * 4, height * 4))

    add_obs(img, ctx, valid)
    func = partial(forecast2image, ctx, valid)
    # We are generally CPU bound here reading those nasty grib2 files :/
    with Pool(4) as pool:
        for fhour, buf in pool.imap_unordered(func, range(1, 16)):
            if buf is None:
                continue
            x = (fhour % 4) * width
            y = (fhour // 4) * height
            bio = BytesIO(buf)
            bio.seek(0)
            with Image.open(bio).resize((512, 386)) as tmp:
                img.paste(tmp, (x, y))

    return img
