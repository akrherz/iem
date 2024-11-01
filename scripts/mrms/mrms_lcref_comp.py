"""
Generate a composite of the MRMS Lowest Composite Reflectvity

called from RUN_1MIN.sh
"""

import gzip
import json
import os
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone

import click
import numpy as np
import pygrib
import pyiem.mrms as mrms
from PIL import Image
from pyiem.reference import ISO8601
from pyiem.util import logger, utc

LOG = logger()


def make_colorramp():
    """
    Make me a crude color ramp
    """
    c = np.zeros((256, 3), int)

    # Gray for missing
    c[255, :] = [144, 144, 144]
    # Black to remove, eventually
    c[0, :] = [0, 0, 0]
    i = 2
    with open("gr2ae.txt", encoding="ascii") as fh:
        for line in fh:
            c[i, :] = list(map(int, line.split()[-3:]))
            i += 1
    return tuple(c.ravel())


def do(now, realtime=False):
    """Generate for this timestep!"""
    szx = 7000
    szy = 3500
    # Create the image data
    imgdata = np.zeros((szy, szx), "u1")
    metadata = {
        "start_valid": now.strftime(ISO8601),
        "end_valid": now.strftime(ISO8601),
        "product": "lcref",
        "units": "0.5 dBZ",
    }

    gribfn = mrms.fetch("SeamlessHSR", now)
    if gribfn is None:
        lf = LOG.warning if realtime else LOG.info
        lf("Missing SeamlessHSR: %s", now.strftime("%Y-%m-%dT%H:%MZ"))
        return

    fp = gzip.GzipFile(gribfn, "rb")
    (_, tmpfn) = tempfile.mkstemp()
    with open(tmpfn, "wb") as fh:
        fh.write(fp.read())
    grbs = pygrib.open(tmpfn)
    grb = grbs[1]
    os.unlink(tmpfn)
    os.unlink(gribfn)

    val = grb["values"]

    # -999 is no coverage, go to 0
    # -99 is missing , go to 255

    val = np.where(val >= -32, (val + 32) * 2.0, val)
    # This is an upstream BUG
    val = np.where(val < 0.0, 0.0, val)
    imgdata[:, :] = np.flipud(val.astype("int"))

    (tmpfp, tmpfn) = tempfile.mkstemp()

    # Create Image
    png = Image.fromarray(np.flipud(imgdata))
    png.putpalette(make_colorramp())
    png.save(f"{tmpfn}.png")

    mrms.write_worldfile(f"{tmpfn}.wld")
    # Inject WLD file
    prefix = "lcref"
    routes = "ac" if realtime else "a"
    pqstr = [
        "pqinsert",
        "-i",
        "-p",
        (
            f"plot {routes} {now:%Y%m%d%H%M} gis/images/4326/mrms/{prefix}.wld"
            f" GIS/mrms/{prefix}_{now:%Y%m%d%H%M}.wld wld"
        ),
        f"{tmpfn}.wld",
    ]
    LOG.info(" ".join(pqstr))
    subprocess.call(pqstr)
    # Now we inject into LDM
    pqstr = [
        "pqinsert",
        "-i",
        "-p",
        (
            f"plot {routes} {now:%Y%m%d%H%M} gis/images/4326/mrms/{prefix}.png"
            f" GIS/mrms/{prefix}_{now:%Y%m%d%H%M}.png png"
        ),
        f"{tmpfn}.png",
    ]
    LOG.info(" ".join(pqstr))
    subprocess.call(pqstr)
    # Create 3857 image
    cmd = [
        "gdalwarp",
        "-s_srs",
        "EPSG:4326",
        "-t_srs",
        "EPSG:3857",
        "-q",
        "-of",
        "GTiff",
        "-tr",
        "1000.0",
        "1000.0",
        f"{tmpfn}.png",
        f"{tmpfn}.tif",
    ]
    subprocess.call(cmd)
    # Insert into LDM
    pqstr = [
        "pqinsert",
        "-i",
        "-p",
        (
            f"plot c {now:%Y%m%d%H%M} gis/images/3857/mrms/{prefix}.tif "
            f"GIS/mrms/{prefix}_{now:%Y%m%d%H%M}.tif tif"
        ),
        f"{tmpfn}.tif",
    ]
    if realtime:
        subprocess.call(pqstr)

    with open(f"{tmpfn}.json", "w", encoding="ascii") as fh:
        json.dump({"meta": metadata}, fh)

    # Insert into LDM
    pqstr = [
        "pqinsert",
        "-p",
        (
            f"plot c {now:%Y%m%d%H%M} gis/images/4326/mrms/{prefix}.json "
            f"GIS/mrms/{prefix}_{now:%Y%m%d%H%M}.json json"
        ),
        f"{tmpfn}.json",
    ]
    if realtime:
        subprocess.call(pqstr)

    for suffix in ["tif", "json", "png", "wld"]:
        os.unlink(f"{tmpfn}.{suffix}")

    os.close(tmpfp)
    os.unlink(tmpfn)


@click.command()
@click.option("--valid", type=click.DateTime())
def main(valid: datetime):
    """Go Main Go"""
    utcnow = utc()
    if valid is not None:
        utcnow = valid.replace(tzinfo=timezone.utc)
        do(utcnow)
    else:
        # If our time is an odd time, run 3 minutes ago
        utcnow = utcnow.replace(second=0, microsecond=0)
        if utcnow.minute % 2 == 1:
            do(utcnow - timedelta(minutes=5), True)


if __name__ == "__main__":
    main()
