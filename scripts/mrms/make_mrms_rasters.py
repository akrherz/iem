"""
 Generate a raster of XXhour precipitation totals from MRMS

 run from RUN_10_AFTER.sh

"""
from __future__ import print_function
import datetime
import os
import sys
import tempfile
import subprocess
import json
import gzip
import unittest

import numpy as np
from PIL import Image
import pyiem.mrms as mrms
import pygrib

TMP = "/mesonet/tmp"
PQI = "pqinsert"
MISSED_FILES = []
DOWNLOADED_FILES = []


def convert_to_image(data):
    """Convert data with units of mm into image space

     255 levels...  wanna do 0 to 20 inches
     index 255 is missing, index 0 is 0
     0-1   -> 100 - 0.01 res ||  0 - 25   -> 100 - 0.25 mm  0
     1-5   -> 80 - 0.05 res  ||  25 - 125 ->  80 - 1.25 mm  100
     5-20  -> 75 - 0.20 res  || 125 - 500  ->  75 - 5 mm    180

    000 -> 099  0.25mm  000.00 to 024.75
    100 -> 179  1.25mm  025.00 to 123.75
    180 -> 254  5.00mm  125.00 to 495.00
    254                 500.00+
    255  MISSING/BAD DATA
    """
    # Values above 500 mm are set to 254
    imgdata = np.where(data >= 500, 254, 0)

    imgdata = np.where(
        np.logical_and(data >= 125, data < 500),
        180 + ((data - 125.0) / 5.0),
        imgdata,
    )
    imgdata = np.where(
        np.logical_and(data >= 25, data < 125),
        100 + ((data - 25.0) / 1.25),
        imgdata,
    )
    imgdata = np.where(
        np.logical_and(data >= 0, data < 25), data / 0.25, imgdata
    )
    # -3 is no coverage -> 255
    # -1 is missing, so zero
    # Index 255 is missing
    imgdata = np.where(data < 0, 0, imgdata)
    imgdata = np.where(data < -1, 255, imgdata)
    return imgdata


def cleanup():
    """Remove tmp downloaded files"""
    for fn in DOWNLOADED_FILES:
        if os.path.isfile(fn):
            os.unlink(fn)


def is_realtime(gts):
    """Is this timestamp a realtime product"""
    utcnow = datetime.datetime.utcnow()
    return utcnow.strftime("%Y%m%d%H") == gts.strftime("%Y%m%d%H")


def doit(gts, hr):
    """
    Actually generate a PNG file from the 8 NMQ tiles
    """
    irealtime = is_realtime(gts)
    routes = "ac" if irealtime else "a"
    sts = gts - datetime.timedelta(hours=hr)
    times = [gts]
    if hr > 24:
        times.append(gts - datetime.timedelta(hours=24))
    if hr == 72:
        times.append(gts - datetime.timedelta(hours=48))
    metadata = {
        "start_valid": sts.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end_valid": gts.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "units": "mm",
    }

    total = None
    mproduct = "RadarOnly_QPE_24H" if hr >= 24 else "RadarOnly_QPE_01H"
    for now in times:
        gribfn = mrms.fetch(mproduct, now)
        if gribfn is None:
            print(
                ("make_mrms_rasters.py[%s] MISSING %s\n  %s\n")
                % (hr, now.strftime("%Y-%m-%dT%H:%MZ"), gribfn)
            )
            MISSED_FILES.append(gribfn)
            return
        DOWNLOADED_FILES.append(gribfn)
        fp = gzip.GzipFile(gribfn, "rb")
        (tmpfp, tmpfn) = tempfile.mkstemp()
        tmpfp = open(tmpfn, "wb")
        tmpfp.write(fp.read())
        tmpfp.close()
        grbs = pygrib.open(tmpfn)
        grb = grbs[1]
        os.unlink(tmpfn)

        # careful here, how we deal with the two missing values!
        if total is None:
            total = grb["values"]
        else:
            maxgrid = np.maximum(grb["values"], total)
            total = np.where(
                np.logical_and(grb["values"] >= 0, total >= 0),
                grb["values"] + total,
                maxgrid,
            )

    imgdata = convert_to_image(total)

    (tmpfp, tmpfn) = tempfile.mkstemp()
    # Create Image
    png = Image.fromarray(imgdata.astype("u1"))
    png.putpalette(mrms.make_colorramp())
    png.save("%s.png" % (tmpfn,))

    if irealtime:
        # create a second PNG with null values set to black
        imgdata = np.where(imgdata == 255, 0, imgdata)
        png = Image.fromarray(imgdata.astype("u1"))
        png.putpalette(mrms.make_colorramp())
        png.save("%s_nn.png" % (tmpfn,))

    # Now we need to generate the world file
    mrms.write_worldfile("%s.wld" % (tmpfn,))
    if irealtime:
        mrms.write_worldfile("%s_nn.wld" % (tmpfn,))
    # Inject WLD file
    pqstr = (
        "%s -i -p 'plot %s %s "
        "gis/images/4326/mrms/p%ih.wld GIS/mrms/p%ih_%s.wld wld' "
        "%s.wld"
        ""
    ) % (
        PQI,
        routes,
        gts.strftime("%Y%m%d%H%M"),
        hr,
        hr,
        gts.strftime("%Y%m%d%H%M"),
        tmpfn,
    )
    subprocess.call(pqstr, shell=True)

    if irealtime:
        pqstr = (
            "%s -i -p 'plot c %s "
            "gis/images/4326/mrms/p%ih_nn.wld "
            "GIS/mrms/p%ih_%s.wld wld' "
            "%s_nn.wld"
            ""
        ) % (
            PQI,
            gts.strftime("%Y%m%d%H%M"),
            hr,
            hr,
            gts.strftime("%Y%m%d%H%M"),
            tmpfn,
        )
        subprocess.call(pqstr, shell=True)

    # Now we inject into LDM
    pqstr = (
        "%s -i -p 'plot %s %s "
        "gis/images/4326/mrms/p%ih.png GIS/mrms/p%ih_%s.png png' "
        "%s.png"
        ""
    ) % (
        PQI,
        routes,
        gts.strftime("%Y%m%d%H%M"),
        hr,
        hr,
        gts.strftime("%Y%m%d%H%M"),
        tmpfn,
    )
    subprocess.call(pqstr, shell=True)

    if irealtime:
        # Now we inject into LDM
        pqstr = (
            "%s -i -p 'plot c %s "
            "gis/images/4326/mrms/p%ih_nn.png "
            "GIS/mrms/p%ih_%s.png png' "
            "%s_nn.png"
            ""
        ) % (
            PQI,
            gts.strftime("%Y%m%d%H%M"),
            hr,
            hr,
            gts.strftime("%Y%m%d%H%M"),
            tmpfn,
        )
        subprocess.call(pqstr, shell=True)

    if irealtime:
        # Create 900913 image
        cmd = (
            "gdalwarp -s_srs EPSG:4326 -t_srs EPSG:3857 -q -of GTiff "
            "-tr 1000.0 1000.0 %s.png %s.tif"
        ) % (tmpfn, tmpfn)
        subprocess.call(cmd, shell=True)

        cmd = (
            "gdalwarp -s_srs EPSG:4326 -t_srs EPSG:3857 -q -of GTiff "
            "-tr 1000.0 1000.0 %s_nn.png %s_nn.tif"
        ) % (tmpfn, tmpfn)
        subprocess.call(cmd, shell=True)

        # Insert into LDM
        pqstr = (
            "%s -i -p 'plot c %s "
            "gis/images/900913/mrms/p%ih.tif "
            "GIS/mrms/p%ih_%s.tif tif' "
            "%s.tif"
            ""
        ) % (
            PQI,
            gts.strftime("%Y%m%d%H%M"),
            hr,
            hr,
            gts.strftime("%Y%m%d%H%M"),
            tmpfn,
        )
        subprocess.call(pqstr, shell=True)

        pqstr = (
            "%s -i -p 'plot c %s "
            "gis/images/900913/mrms/p%ih_nn.tif "
            "GIS/mrms/p%ih_%s.tif tif' "
            "%s_nn.tif"
            ""
        ) % (
            PQI,
            gts.strftime("%Y%m%d%H%M"),
            hr,
            hr,
            gts.strftime("%Y%m%d%H%M"),
            tmpfn,
        )
        subprocess.call(pqstr, shell=True)

        j = open("%s.json" % (tmpfn,), "w")
        j.write(json.dumps(dict(meta=metadata)))
        j.close()

        # Insert into LDM
        pqstr = (
            "%s -i -p 'plot c %s "
            "gis/images/4326/mrms/p%ih.json "
            "GIS/mrms/p%ih_%s.json json'"
            " %s.json"
        ) % (
            PQI,
            gts.strftime("%Y%m%d%H%M"),
            hr,
            hr,
            gts.strftime("%Y%m%d%H%M"),
            tmpfn,
        )
        subprocess.call(pqstr, shell=True)

        pqstr = (
            "%s -i -p 'plot c %s "
            "gis/images/4326/mrms/p%ih_nn.json "
            "GIS/mrms/p%ih_%s.json json'"
            " %s.json"
        ) % (
            PQI,
            gts.strftime("%Y%m%d%H%M"),
            hr,
            hr,
            gts.strftime("%Y%m%d%H%M"),
            tmpfn,
        )
        subprocess.call(pqstr, shell=True)
    for suffix in ["tif", "json", "png", "wld"]:
        fn = "%s.%s" % (tmpfn, suffix)
        if os.path.isfile(fn):
            os.unlink(fn)
    if irealtime:
        for suffix in ["tif", "png", "wld"]:
            fn = "%s_nn.%s" % (tmpfn, suffix)
            if os.path.isfile(fn):
                os.unlink(fn)

    os.close(tmpfp)
    os.unlink(tmpfn)


def main(argv):
    """ We are always explicitly called """
    gts = datetime.datetime(
        int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4]), 0
    )
    for hr in [1, 24, 48, 72]:
        doit(gts, hr)
    cleanup()


if __name__ == "__main__":
    main(sys.argv)


class test(unittest.TestCase):
    """What, test code, Shirely you jest"""

    def test_ramp(self):
        """ Check our work """
        img = convert_to_image(np.array([25]))
        self.assertEquals(img[0], 100)
