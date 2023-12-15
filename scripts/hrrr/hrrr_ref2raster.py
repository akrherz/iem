"""Convert HRRR Grib Reflectivity to RASTERS matching ramp used with N0Q"""
import datetime
import json
import os
import subprocess
import sys
import tempfile

import numpy as np
import pygrib
from PIL import Image
from pyiem.reference import ISO8601
from pyiem.util import logger, utc

LOG = logger()
with open("/mesonet/ldmdata/gis/images/4326/USCOMP/n0q_0.png", "rb") as fh:
    PALETTE = Image.open(fh).getpalette()


def do_grb(grib, valid, routes):
    """Process this grib object"""
    fxdelta = grib.forecastTime
    if grib.fcstimeunits == "mins":
        fxvalid = valid + datetime.timedelta(minutes=fxdelta)
        fxminutes = fxdelta
    else:
        fxvalid = valid + datetime.timedelta(hours=fxdelta)
        fxminutes = int(fxdelta * 60.0)
    newgribtemp = tempfile.NamedTemporaryFile(suffix=".grib2")
    pngtemp = tempfile.NamedTemporaryFile(suffix=".png")
    with tempfile.NamedTemporaryFile(
        suffix=".grib2", delete=False
    ) as gribtemp:
        gribtemp.write(grib.tostring())
    # Regrid this to match N0Q
    cmd = [
        "wgrib2",
        gribtemp.name,
        "-set_grib_type",
        "same",
        "-new_grid_winds",
        "earth",
        "-new_grid",
        "latlon",
        "-126:3050:0.02",
        "23.01:1340:0.02",
        newgribtemp.name,
    ]
    subprocess.call(cmd, stdout=subprocess.PIPE)
    # Rasterize
    grbs = pygrib.open(newgribtemp.name)
    g1 = grbs[1]
    refd = np.flipud(g1.values)
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
    os.unlink(gribtemp.name)
    os.unlink(wldtmp.name)
    os.unlink(jsontmp.name)


def workflow(valid, routes):
    """Process this time's data"""
    gribfn = valid.strftime(
        "/mesonet/ARCHIVE/data/%Y/%m/%d/model/hrrr/%H/hrrr.t%Hz.refd.grib2"
    )
    if not os.path.isfile(gribfn):
        LOG.warning("missing %s", gribfn)
        return
    grbs = pygrib.open(gribfn)
    for i in range(grbs.messages):
        do_grb(grbs[i + 1], valid, routes)


def main(argv):
    """So Something great"""
    valid = utc(int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4]))
    routes = "ac" if argv[5] == "RT" else "a"
    LOG.info("valid: %s routes: %s", valid, routes)
    # See if we already have output
    fn = valid.strftime(
        "/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/hrrr/%H/refd_0000.png"
    )
    if not os.path.isfile(fn):
        workflow(valid, routes)


if __name__ == "__main__":
    main(sys.argv)
