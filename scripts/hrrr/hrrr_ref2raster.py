"""Convert HRRR Grib Reflectivity to RASTERS matching ramp used with N0Q"""

import json
import os
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone

import click
import numpy as np
import pygrib
import pyproj
from affine import Affine
from PIL import Image
from pyiem.reference import ISO8601
from pyiem.util import archive_fetch, logger
from rasterio.warp import reproject

LOG = logger()
with open("/mesonet/ldmdata/gis/images/4326/USCOMP/n0q_0.png", "rb") as fh:
    PALETTE = Image.open(fh).getpalette()


def do_grb(grib, valid, routes):
    """Process this grib object"""
    fxdelta = grib.forecastTime
    if grib.fcstimeunits == "mins":
        fxvalid = valid + timedelta(minutes=fxdelta)
        fxminutes = fxdelta
    else:
        fxvalid = valid + timedelta(hours=fxdelta)
        fxminutes = int(fxdelta * 60.0)
    pngtemp = tempfile.NamedTemporaryFile(suffix=".png")
    projparams = grib.projparams
    lat1 = grib["latitudeOfFirstGridPointInDegrees"]
    lon1 = grib["longitudeOfFirstGridPointInDegrees"]
    llx, lly = pyproj.Proj(projparams)(lon1, lat1)
    hrrr_aff = Affine(
        grib["DxInMetres"],
        0.0,
        llx,
        0.0,
        grib["DyInMetres"],
        lly,
    )
    dest_aff = Affine(0.02, 0.0, -126.0, 0.0, -0.02, 50.0)
    refd = np.zeros((1340, 3050))
    reproject(
        grib.values,
        refd,
        src_transform=hrrr_aff,
        src_crs=projparams,
        dst_transform=dest_aff,
        dst_crs="EPSG:4326",
        dst_nodata=-99,
    )
    # anything -10 or lower is zero
    refd = np.where(refd < -9, -99, refd)
    # rasterize from index 1 as -32 by 0.5
    raster = (refd + 32.0) * 2.0 + 1
    raster = np.where(
        np.logical_or(raster < 1, raster > 255), 0, raster
    ).astype(np.uint8)
    png = Image.fromarray(raster)
    png.putpalette(PALETTE)
    png.save(pngtemp)
    cmd = [
        "pqinsert",
        "-i",
        "-p",
        (
            f"plot {routes} {valid:%Y%m%d%H%M} gis/images/4326/hrrr/"
            f"refd_{fxminutes:04.0f}.png GIS/hrrr/{valid:%H}/"
            f"refd_{fxminutes:04.0f}.png png"
        ),
        pngtemp.name,
    ]
    subprocess.call(cmd)
    # Do world file variant
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as wldtmp:
        wldtmp.write(
            "\n".join(["0.02", "0.0", "0.0", "-0.02", "-126.0", "50.0"])
        )
    cmd = [
        "pqinsert",
        "-i",
        "-p",
        (
            f"plot {routes} {valid:%Y%m%d%H%M} gis/images/4326/hrrr/"
            f"refd_{fxminutes:04.0f}.wld GIS/hrrr/{valid:%H}/"
            f"refd_{fxminutes:04.0f}.wld wld"
        ),
        wldtmp.name,
    ]
    subprocess.call(cmd)
    # Do json metadata
    jdict = {
        "model_init_utc": valid.strftime(ISO8601),
        "forecast_minute": fxminutes,
        "model_forecast_utc": fxvalid.strftime(ISO8601),
    }
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as jsontmp:
        json.dump(jdict, jsontmp)
    # No need to archive this JSON file, it provides nothing new
    cmd = [
        "pqinsert",
        "-i",
        "-p",
        (
            f"plot c {valid:%Y%m%d%H%M} gis/images/4326/hrrr/"
            f"refd_{fxminutes:04.0f}.json bogus json"
        ),
        jsontmp.name,
    ]
    if routes == "ac":
        subprocess.call(cmd)
    os.unlink(wldtmp.name)
    os.unlink(jsontmp.name)


def workflow(valid: datetime, routes: str):
    """Process this time's data"""
    ppath = valid.strftime("%Y/%m/%d/model/hrrr/%H/hrrr.t%Hz.refd.grib2")
    with archive_fetch(ppath) as fn:
        if fn is None:
            LOG.warning("missing %s", ppath)
            return
        with pygrib.open(fn) as grbs:
            for grb in grbs:
                if grb.shortName == "refd":
                    do_grb(grb, valid, routes)


@click.command()
@click.option("--valid", type=click.DateTime(), required=True)
@click.option("--is-realtime", "rt", is_flag=True)
def main(valid: datetime, rt: bool):
    """So Something great"""
    valid = valid.replace(tzinfo=timezone.utc)
    LOG.info("valid: %s realtime: %s", valid, rt)
    routes = "ac" if rt else "a"
    # See if we already have output
    ppath = valid.strftime("%Y/%m/%d/GIS/hrrr/%H/refd_0000.png")
    with archive_fetch(ppath) as fn:
        if fn is None:
            workflow(valid, routes)


if __name__ == "__main__":
    main()
