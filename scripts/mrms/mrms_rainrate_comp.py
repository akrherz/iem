"""Generate a composite of the MRMS PrecipRate

Within a two minute window, maybe the max rate we could see is 0.2 inches,
which is 5 mm.  So if we want to store 5mm in 250 bins, we have a resolution
of 0.02 mm per index.

Run from RUN_1MIN.sh
"""

import datetime
import gzip
import json
import os
import subprocess
import tempfile

import click
import numpy as np
import pygrib
from PIL import Image
from pyiem import mrms
from pyiem.reference import ISO8601
from pyiem.util import archive_fetch, logger, utc

LOG = logger()


def workflow(now, realtime):
    """Generate for this timestep!"""
    minutes = 2 if now.year > 2011 else 5
    szx = 7000
    szy = 3500
    # Create the image data
    imgdata = np.zeros((szy, szx), "u1")
    sts = now - datetime.timedelta(minutes=2)
    prefix = f"a{minutes}m"
    metadata = {
        "start_valid": sts.strftime(ISO8601),
        "end_valid": now.strftime(ISO8601),
        "product": prefix,
        "units": "0.02 mm",
    }

    gribfn = mrms.fetch("PrecipRate", now)
    if gribfn is None:
        lf = LOG.warning if realtime else LOG.info
        lf("Missing PrecipRate: %s", now.strftime("%Y-%m-%dT%H:%MZ"))
        return

    # http://www.nssl.noaa.gov/projects/mrms/operational/tables.php
    # Says units are mm/hr
    fp = gzip.GzipFile(gribfn, "rb")
    (_, tmpfn) = tempfile.mkstemp()
    with open(tmpfn, "wb") as fh:
        try:
            fh.write(fp.read())
        except EOFError:
            LOG.info("caught EOFError on %s, likely corrupt, deleting", gribfn)
            os.unlink(gribfn)
            return
    grbs = pygrib.open(tmpfn)
    grb = grbs[1]
    os.unlink(tmpfn)
    os.unlink(gribfn)

    val = grb["values"]
    # If has a mask, convert those to -3
    if hasattr(val, "mask"):
        val = np.where(val.mask, -3, val)
    # Convert into units of 0.02 mm accumulation
    val = val / 60.0 * minutes * 50.0
    val = np.where(val < 0.0, 255.0, val)
    imgdata[:, :] = np.flipud(val.astype("int"))

    (tmpfp, tmpfn) = tempfile.mkstemp()

    # Create Image
    png = Image.fromarray(np.flipud(imgdata))
    png.putpalette(mrms.make_colorramp())
    png.save(f"{tmpfn}.png")

    mrms.write_worldfile(f"{tmpfn}.wld")
    # Inject WLD file
    routes = "c" if realtime else ""
    cmd = [
        "pqinsert",
        "-i",
        "-p",
        f"plot a{routes} {now:%Y%m%d%H%M} "
        f"gis/images/4326/mrms/{prefix}.wld GIS/mrms/{prefix}_"
        f"{now:%Y%m%d%H%M}.wld wld",
        f"{tmpfn}.wld",
    ]
    subprocess.call(cmd)
    # Now we inject into LDM
    cmd = [
        "pqinsert",
        "-i",
        "-p",
        f"plot a{routes} {now:%Y%m%d%H%M} "
        f"gis/images/4326/mrms/{prefix}.png GIS/mrms/{prefix}_"
        f"{now:%Y%m%d%H%M}.png png",
        f"{tmpfn}.png",
    ]
    subprocess.call(cmd)

    if realtime:
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
        cmd = [
            "pqinsert",
            "-i",
            "-p",
            f"plot c {now:%Y%m%d%H%M} gis/images/3857/mrms/{prefix}.tif "
            f"GIS/mrms/{prefix}_{now:%Y%m%d%H%M}.tif tif",
            f"{tmpfn}.tif",
        ]
        subprocess.call(cmd)

        with open(f"{tmpfn}.json", "w", encoding="utf8") as fh:
            json.dump({"meta": metadata}, fh)
        # Insert into LDM
        cmd = [
            "pqinsert",
            "-i",
            "-p",
            f"plot c {now:%Y%m%d%H%M} gis/images/4326/mrms/{prefix}.json "
            f"GIS/mrms/{prefix}_{now:%Y%m%d%H%M}.json json",
            f"{tmpfn}.json",
        ]
        subprocess.call(cmd)
    for suffix in ["tif", "json", "png", "wld"]:
        if os.path.isfile(f"{tmpfn}.{suffix}"):
            os.unlink(f"{tmpfn}.{suffix}")

    os.close(tmpfp)
    os.unlink(tmpfn)


@click.command()
@click.option("--valid", type=click.DateTime(), help="UTC Timestamp")
def main(valid):
    """Go Main Go"""
    valid = valid.replace(tzinfo=datetime.timezone.utc)
    realtime = False
    if utc() - valid < datetime.timedelta(minutes=10):
        realtime = True
    # Present reality
    if realtime and valid.minute % 2 != 0:
        LOG.info("Skipping realtime %s as minute not even", valid)
        return
    workflow(valid, True)
    # Also check old dates
    for delta in [30, 90, 600, 1440, 2880]:
        ts = valid - datetime.timedelta(minutes=delta)
        ppath = ts.strftime("%Y/%m/%d/GIS/mrms/a2m_%Y%m%d%H%M.png")
        with archive_fetch(ppath) as fn:
            if fn is None:
                workflow(ts, False)


if __name__ == "__main__":
    main()
