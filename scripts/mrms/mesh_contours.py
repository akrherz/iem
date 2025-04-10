"""Generate MRMS MESH Contours.

dedicated crontab entry.
"""

import json
import os
import pathlib
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone

import click
import numpy as np
import pygrib
import rasterio
from pyiem.mrms import NORTH, WEST
from pyiem.reference import ISO8601
from pyiem.util import logger, utc
from rasterio.transform import from_origin

LOG = logger()
VERSION = 1


def pqinsert(tmpfn, ets, interval):
    """pqinsert the GeoJSON."""
    routes = "ac" if (interval in (60, 1440) and ets.minute == 0) else "c"

    name = (
        f"data {routes} {ets.strftime('%Y%m%d%H%M')} "
        f"gis/shape/4326/us/mrms_mesh_{interval}min.geojson "
        f"GIS/mrms/mesh_{interval}min_{ets.strftime('%Y%m%d%H%M')}.geojson "
        "bogus"
    )
    LOG.info(name)
    cmd = ["pqinsert", "-i", "-p", name, f"{tmpfn}.geojson"]
    if pathlib.Path(f"{tmpfn}.geojson").stat().st_size > 0:
        subprocess.call(cmd)
    cmd = [
        "pqinsert",
        "-i",
        "-p",
        name.replace(".geojson", "_meta.json"),
        f"{tmpfn}_meta.json",
    ]
    subprocess.call(cmd)


def make_metadata(tmpfn, mydict):
    """Make metadata."""
    with open(f"{tmpfn}_meta.json", "w") as fp:  # skipcq
        json.dump(mydict, fp)


def make_contours(tmpfn):
    """Make a GeoJSON."""
    cmd = [
        "timeout",
        "120",
        "gdal_contour",
        "-fl",
        " ".join(str(x) for x in range(0, 101, 5)) + " 150 200",
        "-amin",
        "ssize_mm",
        "-amax",
        "esize_mm",
        "-snodata",
        "-1",
        "-p",
        "-q",
        f"{tmpfn}.tif",
        f"{tmpfn}.geojson",
    ]
    with subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ) as proc:
        (stdout, stderr) = proc.communicate()
    if stdout != b"" or stderr != b"":
        LOG.info("stdout: %s stderr: %s", stdout, stderr)


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
    interval = timedelta(minutes=2)
    # in the rears
    now = sts + timedelta(minutes=2)
    maxval = None
    hits = 0
    misses = 0
    while now <= ets:
        fn = now.strftime("/mnt/mrms/MESH/%d%H%M.grib")
        if os.path.isfile(fn):
            with pygrib.open(fn) as grb:
                if maxval is None:
                    maxval = grb[1].values
                else:
                    maxval = np.maximum(grb[1].values, maxval)
            hits += 1
        else:
            misses += 1
        now += interval
    return maxval, hits, misses


@click.command()
@click.option("--minutes", required=True, type=int)
@click.option("--valid", required=True, type=click.DateTime())
def main(minutes: int, valid: datetime):
    """Go Main Go."""
    started = utc()
    valid = valid.replace(tzinfo=timezone.utc)
    ets = valid
    sts = ets - timedelta(minutes=minutes)
    with tempfile.NamedTemporaryFile() as tmp:
        maxval, hits, misses = agg(sts, ets)
        if maxval is None:
            LOG.info("Aborting, no data! %s %s", minutes, valid)
            return
        make_raster(maxval, tmp.name)
        make_contours(tmp.name)
        os.unlink(f"{tmp.name}.tif")
        mydict = {
            "generated_at": utc().strftime(ISO8601),
            "start_time_utc": sts.strftime(ISO8601),
            "end_time_utc": ets.strftime(ISO8601),
            "2min_files_used": hits,
            "2min_files_missed": misses,
            "script_version": VERSION,
            "script_time_s": (utc() - started).total_seconds(),
        }
        make_metadata(tmp.name, mydict)
        pqinsert(tmp.name, ets, minutes)
        os.unlink(f"{tmp.name}.geojson")
        os.unlink(f"{tmp.name}_meta.json")


if __name__ == "__main__":
    main()
