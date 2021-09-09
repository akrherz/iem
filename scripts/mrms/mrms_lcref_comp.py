"""
 Generate a composite of the MRMS Lowest Composite Reflectvity
"""
import datetime
import os
import tempfile
import json
import sys
import gzip
import subprocess

import numpy as np
from PIL import Image
import pygrib
import pyiem.mrms as mrms
from pyiem.util import utc, logger

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
    for line in open("gr2ae.txt").readlines():
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
        "start_valid": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end_valid": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "product": "lcref",
        "units": "0.5 dBZ",
    }

    gribfn = mrms.fetch("SeamlessHSR", now)
    if gribfn is None:
        print(
            ("mrms_lcref_comp.py NODATA for SeamlessHSR: %s")
            % (now.strftime("%Y-%m-%dT%H:%MZ"),)
        )
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
    # val = np.where(val < -990., 0., val)
    # val = np.where(val < -90., 255., val)
    # This is an upstream BUG
    val = np.where(val < 0.0, 0.0, val)
    imgdata[:, :] = np.flipud(val.astype("int"))

    (tmpfp, tmpfn) = tempfile.mkstemp()

    # Create Image
    png = Image.fromarray(np.flipud(imgdata))
    png.putpalette(make_colorramp())
    png.save("%s.png" % (tmpfn,))

    mrms.write_worldfile("%s.wld" % (tmpfn,))
    # Inject WLD file
    prefix = "lcref"
    routes = "ac" if realtime else "a"
    pqstr = (
        "pqinsert -i -p 'plot %s %s "
        "gis/images/4326/mrms/%s.wld GIS/mrms/%s_%s.wld wld' %s.wld"
    ) % (
        routes,
        now.strftime("%Y%m%d%H%M"),
        prefix,
        prefix,
        now.strftime("%Y%m%d%H%M"),
        tmpfn,
    )
    LOG.debug(pqstr)
    subprocess.call(pqstr, shell=True)
    # Now we inject into LDM
    pqstr = (
        "pqinsert -i -p 'plot %s %s "
        "gis/images/4326/mrms/%s.png GIS/mrms/%s_%s.png png' %s.png"
    ) % (
        routes,
        now.strftime("%Y%m%d%H%M"),
        prefix,
        prefix,
        now.strftime("%Y%m%d%H%M"),
        tmpfn,
    )
    LOG.debug(pqstr)
    subprocess.call(pqstr, shell=True)
    # Create 3857 image
    cmd = (
        "gdalwarp -s_srs EPSG:4326 -t_srs EPSG:3857 -q -of GTiff "
        "-tr 1000.0 1000.0 %s.png %s.tif"
    ) % (tmpfn, tmpfn)
    subprocess.call(cmd, shell=True)
    # Insert into LDM
    pqstr = (
        "pqinsert -i -p 'plot c %s "
        "gis/images/3857/mrms/%s.tif GIS/mrms/%s_%s.tif tif' %s.tif"
    ) % (
        now.strftime("%Y%m%d%H%M"),
        prefix,
        prefix,
        now.strftime("%Y%m%d%H%M"),
        tmpfn,
    )
    if realtime:
        LOG.debug(pqstr)
        subprocess.call(pqstr, shell=True)

    with open("%s.json" % (tmpfn,), "w") as fh:
        fh.write(json.dumps(dict(meta=metadata)))

    # Insert into LDM
    pqstr = (
        "pqinsert -p 'plot c %s "
        "gis/images/4326/mrms/%s.json GIS/mrms/%s_%s.json json' %s.json"
    ) % (
        now.strftime("%Y%m%d%H%M"),
        prefix,
        prefix,
        now.strftime("%Y%m%d%H%M"),
        tmpfn,
    )
    if realtime:
        LOG.debug(pqstr)
        subprocess.call(pqstr, shell=True)

    for suffix in ["tif", "json", "png", "wld"]:
        os.unlink(f"{tmpfn}.{suffix}")

    os.close(tmpfp)
    os.unlink(tmpfn)


def main(argv):
    """Go Main Go"""
    utcnow = utc()
    if len(argv) == 6:
        utcnow = utc(
            int(argv[1]),
            int(argv[2]),
            int(argv[3]),
            int(argv[4]),
            int(argv[5]),
        )
        do(utcnow)
    else:
        # If our time is an odd time, run 3 minutes ago
        utcnow = utcnow.replace(second=0, microsecond=0)
        if utcnow.minute % 2 == 1:
            do(utcnow - datetime.timedelta(minutes=5), True)


if __name__ == "__main__":
    # Lets do something
    main(sys.argv)
