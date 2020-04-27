"""Generate MRMS MESH Contours."""
import argparse
import datetime
import json
import os
import subprocess
import sys
import tempfile

import pygrib
import numpy as np
from pyiem.util import logger
from pyiem.mrms import NORTH, WEST
import rasterio
from rasterio.transform import from_origin

LOG = logger()
VERSION = 1
ISO9660 = "%Y-%m-%dT%H:%M:00Z"


def pqinsert(tmpfn, ets, interval):
    """pqinsert the GeoJSON."""
    routes = "ac" if (interval in (60, 1440) and ets.minute == 0) else "c"

    name = (
        f"data {routes} {ets.strftime('%Y%m%d%H%M')} "
        f"gis/shape/4326/us/mrms_mesh_{interval}min.geojson "
        f"GIS/mrms/mesh_{interval}min_{ets.strftime('%Y%m%d%H%M')}.geojson "
        "bogus"
    )
    LOG.debug(name)
    cmd = f"pqinsert -i -p '{name}' {tmpfn}.geojson"
    subprocess.call(cmd, shell=True)
    cmd = (
        f"pqinsert -i -p '{name.replace('.geojson', '_meta.json')}' "
        f"{tmpfn}_meta.json"
    )
    subprocess.call(cmd, shell=True)


def make_metadata(tmpfn, mydict):
    """Make metadata."""
    with open(f"{tmpfn}_meta.json", "w") as fp:
        fp.write(json.dumps(mydict))


def make_contours(tmpfn):
    """Make a GeoJSON."""
    cmd = (
        "gdal_contour -fl 0 5 10 15 20 25 30 35 40 45 50 55 60 65 70 75 80 85 "
        "90 95 100 150 200 -amin ssize_mm -amax esize_mm "
        f"-snodata -1 -p -q {tmpfn}.tif {tmpfn}.geojson"
    )
    subprocess.call(cmd, shell=True)


def make_raster(vals, tmpfn):
    """Make a TIFF for downstream gdal_contour usage."""
    vals = np.where(vals < 0, -1, vals)
    transform = from_origin(WEST, NORTH, 0.01, 0.01)
    with rasterio.open(
        f"{tmpfn}.tif",
        "w",
        driver="GTiff",
        height=vals.shape[0],
        width=vals.shape[1],
        count=1,
        dtype=str(vals.dtype),
        crs="+proj=longlat +datum=WGS84 +no_defs",
        transform=transform,
    ) as rst:
        rst.write(vals, 1)


def agg(sts, ets):
    """Aggregate up the value."""
    interval = datetime.timedelta(minutes=2)
    # in the rears
    now = sts + datetime.timedelta(minutes=2)
    maxval = None
    hits = 0
    misses = 0
    while now <= ets:
        fn = now.strftime("/mnt/mrms/MESH/%d%H%M.grib")
        if os.path.isfile(fn):
            grb = pygrib.open(fn)
            if maxval is None:
                maxval = grb[1].values
            else:
                maxval = np.maximum(grb[1].values, maxval)
            hits += 1
        else:
            misses += 1
        now += interval
    return maxval, hits, misses


def usage():
    """Create the argparse instance."""
    parser = argparse.ArgumentParser("MRMS MRSH Contours")
    parser.add_argument("-i", "--interval", required=True, type=int)
    parser.add_argument(
        "-t",
        "--datetime",
        required=True,
        type=lambda d: datetime.datetime.strptime(d[:16], "%Y-%m-%dT%H:%M"),
    )
    return parser


def main(argv):
    """Go Main Go."""
    started = datetime.datetime.utcnow()
    ctx = usage().parse_args(argv[1:])
    ets = ctx.datetime
    sts = ets - datetime.timedelta(minutes=ctx.interval)
    with tempfile.NamedTemporaryFile() as tmp:
        maxval, hits, misses = agg(sts, ets)
        if maxval is None:
            LOG.info("Aborting, no data! %s", ctx)
            return
        make_raster(maxval, tmp.name)
        make_contours(tmp.name)
        os.unlink(f"{tmp.name}.tif")
        mydict = {
            "generated_at": datetime.datetime.utcnow().strftime(ISO9660),
            "start_time_utc": sts.strftime(ISO9660),
            "end_time_utc": ets.strftime(ISO9660),
            "2min_files_used": hits,
            "2min_files_missed": misses,
            "script_version": VERSION,
            "script_time_s": (
                datetime.datetime.utcnow() - started
            ).total_seconds(),
        }
        make_metadata(tmp.name, mydict)
        pqinsert(tmp.name, ets, ctx.interval)
        os.unlink(f"{tmp.name}.geojson")


if __name__ == "__main__":
    main(sys.argv)
