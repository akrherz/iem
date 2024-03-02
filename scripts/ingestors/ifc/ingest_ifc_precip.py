"""
  Process the IFC precip data!  Here's the file header
# file name: H99999999_I0007_G_15MAR2013_154000.out
# Rainrate map [mm/hr]
# number of columns: 1741
# number of rows: 1057
# grid: LATLON
# upper-left LATLONcorner(x,y): 6924 5409
# xllcorner [lon]: -97.154167
# yllcorner [lat]: 40.133331
# cellsize [dec deg]: 0.004167
# no data value: -99.0

http://s-iihr57.iihr.uiowa.edu/feeds/IFC7ADV/latest.dat
http://s-iihr57.iihr.uiowa.edu/feeds/IFC7ADV/H99999999_I0007_G_15MAR2013_154500.out
"""

import datetime
import os
import subprocess
import tempfile

import numpy as np
import pyiem.mrms as mrms
import requests
from PIL import Image, PngImagePlugin
from pyiem.util import exponential_backoff, logger

LOG = logger()
BASEURL = "http://s-iihr77.iihr.uiowa.edu//Products/IFC7ADV"


def get_file(tmpdir, now, routes):
    """Download the file, save to /tmp and return fn"""
    data = None
    for i in [7, 6, 5, 4]:
        if data is not None:
            break
        fn = now.strftime(
            ("H99999999_I000" + repr(i) + "_G_%d%b%Y" "_%H%M00")
        ).upper()
        uri = f"{BASEURL}/{fn}.out"
        req = exponential_backoff(requests.get, uri, timeout=5)
        if req is None:
            continue
        if req.status_code == 404:
            continue
        if req.status_code != 200:
            LOG.info("uri %s failed with status %s", uri, req.status_code)
            continue
        data = req.text

    if data is None:
        # only generate an annoy-o-gram if we are in archive mode
        if routes == "a":
            LOG.info("missing data for %s", now)
        return None
    fn = f"{tmpdir}/{fn}.out"
    with open(fn, "w", encoding="ascii") as fh:
        fh.write(data)
    return fn


def to_raster(tmpfn, now):
    """Convert the raw data into a RASTER Image
    5 inch rain per hour is ~ 125 mm/hr, so over 5min that is 10 mm
    Index 255 is missing
    0 is zero
    1 is 0.1 mm
    254 is 25.4 mm
    """
    data = np.loadtxt(tmpfn, skiprows=10)
    # mm/hr to mm/5min
    imgdata = data * 10.0 / 12.0
    imgdata = np.where(imgdata < 0, 255, imgdata)
    png = Image.fromarray(np.uint8(imgdata))
    png.putpalette(mrms.make_colorramp())
    meta = PngImagePlugin.PngInfo()
    meta.add_text("title", now.strftime("%Y%m%d%H%M"), 0)
    png.save(f"{tmpfn}.png", pnginfo=meta)
    del png
    # Make worldfile
    with open(f"{tmpfn}.wld", "w") as fh:
        fh.write(
            "0.004167\n"
            "0.00\n"
            "0.00\n"
            "-0.004167\n"
            "44.53785\n"
            "-89.89942"
        )


def ldm(tmpfn, now, routes):
    """Send stuff to ldm"""
    for suffix in ["png", "wld"]:
        cmd = [
            "pqinsert",
            "-i",
            "-p",
            f"plot {routes} {now:%Y%m%d%H%M} "
            f"gis/images/4326/ifc/p05m.{suffix} "
            f"GIS/ifc/p05m_{now:%Y%m%d%H%M}.{suffix} {suffix}",
            f"{tmpfn}.{suffix}",
        ]
        LOG.info(" ".join(cmd))
        subprocess.call(cmd)


def do_time(tmpdir, now, routes="ac"):
    """workflow"""
    tmpfn = get_file(tmpdir, now, routes)
    if tmpfn is None:
        LOG.info("tmpfn is None, returning")
        return

    to_raster(tmpfn, now)

    ldm(tmpfn, now, routes)


def main():
    """main method"""
    now = datetime.datetime.utcnow()
    now = now.replace(second=0, microsecond=0)
    # Round back to the nearest 5 minute, plus 10
    delta = now.minute % 5 + 15
    now = now - datetime.timedelta(minutes=delta)

    with tempfile.TemporaryDirectory() as tmpdir:
        do_time(tmpdir, now)
    # Do we need to rerun a previous hour
    now = now - datetime.timedelta(minutes=60)
    fn = now.strftime(
        "/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/ifc/p05m_%Y%m%d%H%M.png"
    )
    if not os.path.isfile(fn):
        with tempfile.TemporaryDirectory() as tmpdir:
            do_time(tmpdir, now, routes="a")


if __name__ == "__main__":
    main()
