"""Convert HRRR Grib Reflectivity to RASTERS matching ramp used with N0Q"""

import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import click
import numpy as np
import pandas as pd
import pyproj
import xarray as xr
from affine import Affine
from matplotlib.colors import hex2color
from PIL import Image
from pyiem.plot.colormaps import radar_ptype
from pyiem.reference import ISO8601
from pyiem.util import archive_fetch, logger
from rasterio.warp import reproject

LOG = logger()
with open("/mesonet/ldmdata/gis/images/4326/USCOMP/n0q_0.png", "rb") as fh:
    PALETTE = Image.open(fh).getpalette()


def do_step(
    ds: xr.Dataset,
    step: int,
    toffset: np.timedelta64,
    routes: str,
    ptype: bool,
):
    """Process the timestep."""
    valid = (
        pd.Timestamp(ds.time.values)
        .to_pydatetime()
        .replace(tzinfo=ZoneInfo("UTC"))
    )
    fxvalid = (
        pd.Timestamp(ds.time.values + toffset)
        .to_pydatetime()
        .replace(tzinfo=ZoneInfo("UTC"))
    )
    fxminutes = toffset / np.timedelta64(1, "m")
    LOG.info("Processing %s %s %s", valid, fxvalid, fxminutes)

    if ptype:
        raw = np.ma.masked_where(ds.refd[step] < 5, ds.refd[step])
        # Cap values at 55 dBz and we can't have 55 either
        raw = np.ma.where(raw > 54.9, 54.9, raw)
        label = "refp"
    else:
        raw = ds.refd[step]
        label = "refd"
    pstep = max(step, 1)

    pngtemp = tempfile.NamedTemporaryFile(suffix=".png")
    projparams = {
        "proj": "lcc",
        "lat_1": ds.refd.GRIB_Latin1InDegrees,
        "lat_2": ds.refd.GRIB_Latin2InDegrees,
        "lat_0": ds.refd.GRIB_LaDInDegrees,
        "lon_0": ds.refd.GRIB_LoVInDegrees,
    }
    lat1 = ds.refd.GRIB_latitudeOfFirstGridPointInDegrees
    lon1 = ds.refd.GRIB_longitudeOfFirstGridPointInDegrees
    llx, lly = pyproj.Proj(projparams)(lon1, lat1)
    hrrr_aff = Affine(
        ds.refd.GRIB_DxInMetres,
        0.0,
        llx,
        0.0,
        ds.refd.GRIB_DyInMetres,
        lly,
    )
    dest_aff = Affine(0.02, 0.0, -126.0, 0.0, -0.02, 50.0)
    if ptype:
        refidx = np.zeros(raw.shape)
        color_ramps = radar_ptype()
        colors = ["#000000"]
        color_index_start = 1
        for typ in ["rain", "snow", "frzr", "icep"]:
            colors.extend(color_ramps[typ])
            # Each ramp colors from 0 to 55 by 2.5 dbz
            refidx = np.ma.where(
                ds[f"c{typ}"][pstep] > 0.01,
                raw / 2.5 + color_index_start,
                refidx,
            )
            color_index_start += len(color_ramps[typ])
        raw = refidx
    refd = np.zeros((1340, 3050))
    reproject(
        raw,
        refd,
        src_transform=hrrr_aff,
        src_crs=projparams,
        dst_transform=dest_aff,
        dst_crs="EPSG:4326",
        dst_nodata=-99,
    )
    if not ptype:
        # anything -10 or lower is zero
        refd = np.where(refd < -9, -99, refd)
        # rasterize from index 1 as -32 by 0.5
        raster = (refd + 32.0) * 2.0 + 1
        raster = np.where(
            np.logical_or(raster < 1, raster > 255), 0, raster
        ).astype(np.uint8)
        palette = PALETTE
    else:
        raster = refd.astype(np.uint8)
        palette = []
        for c in colors:
            (r, g, b) = hex2color(c)
            palette.extend([int(r * 255), int(g * 255), int(b * 255)])
    png = Image.fromarray(raster)
    png.putpalette(palette)
    png.save(pngtemp)
    cmd = [
        "pqinsert",
        "-i",
        "-p",
        (
            f"plot {routes} {valid:%Y%m%d%H%M} gis/images/4326/hrrr/"
            f"{label}_{fxminutes:04.0f}.png GIS/hrrr/{valid:%H}/"
            f"{label}_{fxminutes:04.0f}.png png"
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
            f"{label}_{fxminutes:04.0f}.wld GIS/hrrr/{valid:%H}/"
            f"{label}_{fxminutes:04.0f}.wld wld"
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
            f"{label}_{fxminutes:04.0f}.json bogus json"
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
        ds = xr.open_dataset(fn)
        for step, toffset in enumerate(ds.step.values):
            do_step(ds, step, toffset, routes, False)
            do_step(ds, step, toffset, routes, True)


@click.command()
@click.option("--valid", type=click.DateTime(), required=True)
@click.option("--is-realtime", "rt", is_flag=True)
@click.option("--force", default=False, is_flag=True)
def main(valid: datetime, rt: bool, force: bool):
    """So Something great"""
    valid = valid.replace(tzinfo=timezone.utc)
    LOG.info("valid: %s realtime: %s", valid, rt)
    routes = "ac" if rt else "a"
    # See if we already have output
    ppath = valid.strftime("%Y/%m/%d/GIS/hrrr/%H/refd_0000.png")
    with archive_fetch(ppath) as fn:
        if fn is not None and not force:
            return
    workflow(valid, routes)


if __name__ == "__main__":
    main()
