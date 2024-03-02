"""
Generate a raster of XXhour precipitation totals from MRMS

run from RUN_10_AFTER.sh

"""

import datetime
import gzip
import json
import os
import subprocess
import sys
import tempfile

import numpy as np
import pygrib
from PIL import Image
from pyiem import mrms
from pyiem.reference import ISO8601
from pyiem.util import logger

LOG = logger()
TMP = "/mesonet/tmp"
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


def need_not_run(gts, hr) -> bool:
    """Do we need to run for this combination?"""
    testfn = (
        f"/mesonet/ARCHIVE/data/{gts:%Y/%m/%d}/GIS/mrms/p{hr}h_"
        f"{gts:%Y%m%d%H%M}.png"
    )
    return os.path.isfile(testfn)


def doit(gts, hr):
    """
    Actually generate a PNG file from the 8 NMQ tiles
    """
    irealtime = is_realtime(gts)
    if not irealtime:
        if need_not_run(gts, hr):
            LOG.info("Skipping as archive file exists")
            return
        LOG.warning("Reprocessing %s[%s] due to missing archive.", gts, hr)
    routes = "ac" if irealtime else "a"
    sts = gts - datetime.timedelta(hours=hr)
    times = [gts]
    if hr > 24:
        times.append(gts - datetime.timedelta(hours=24))
    if hr == 72:
        times.append(gts - datetime.timedelta(hours=48))
    metadata = {
        "start_valid": sts.strftime(ISO8601),
        "end_valid": gts.strftime(ISO8601),
        "units": "mm",
    }

    total = None
    mproduct = "RadarOnly_QPE_24H" if hr >= 24 else "RadarOnly_QPE_01H"
    for now in times:
        gribfn = mrms.fetch(mproduct, now)
        if gribfn is None:
            LOG.warning(
                "%s MISSING %s\n  %s\n",
                hr,
                now.strftime("%Y-%m-%dT%H:%MZ"),
                gribfn,
            )
            MISSED_FILES.append(gribfn)
            return
        DOWNLOADED_FILES.append(gribfn)
        (tmpfp, tmpfn) = tempfile.mkstemp()
        with gzip.GzipFile(gribfn, "rb") as fp:
            with open(tmpfn, "wb") as tmpfp:
                tmpfp.write(fp.read())
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
    png.save(f"{tmpfn}.png")

    if irealtime:
        # create a second PNG with null values set to black
        imgdata = np.where(imgdata == 255, 0, imgdata)
        png = Image.fromarray(imgdata.astype("u1"))
        png.putpalette(mrms.make_colorramp())
        png.save(f"{tmpfn}_nn.png")

    # Now we need to generate the world file
    mrms.write_worldfile(f"{tmpfn}.wld")
    if irealtime:
        mrms.write_worldfile(f"{tmpfn}_nn.wld")
    # Inject WLD file
    tstr = gts.strftime("%Y%m%d%H%M")
    cmd = (
        f"pqinsert -i -p 'plot {routes} {tstr} "
        f"gis/images/4326/mrms/p{hr}h.wld GIS/mrms/p{hr}h_{tstr}.wld wld' "
        f"{tmpfn}.wld"
    )
    subprocess.call(cmd, shell=True)

    if irealtime:
        pqstr = (
            f"pqinsert -i -p 'plot c {tstr} "
            f"gis/images/4326/mrms/p{hr}h_nn.wld "
            f"GIS/mrms/p{hr}h_{tstr}.wld wld' "
            f"{tmpfn}_nn.wld"
        )
        subprocess.call(pqstr, shell=True)

    # Now we inject into LDM
    pqstr = (
        f"pqinsert -i -p 'plot {routes} {tstr} "
        f"gis/images/4326/mrms/p{hr}h.png GIS/mrms/p{hr}h_{tstr}.png png' "
        f"{tmpfn}.png"
    )
    subprocess.call(pqstr, shell=True)

    if irealtime:
        # Now we inject into LDM
        pqstr = (
            f"pqinsert -i -p 'plot c {tstr} "
            f"gis/images/4326/mrms/p{hr}h_nn.png "
            f"GIS/mrms/p{hr}h_{tstr}.png png' {tmpfn}_nn.png"
        )
        subprocess.call(pqstr, shell=True)

        # Create 3857 image
        cmd = (
            "gdalwarp -s_srs EPSG:4326 -t_srs EPSG:3857 -q -of GTiff "
            f"-tr 1000.0 1000.0 {tmpfn}.png {tmpfn}.tif"
        )
        subprocess.call(cmd, shell=True)

        cmd = (
            "gdalwarp -s_srs EPSG:4326 -t_srs EPSG:3857 -q -of GTiff "
            f"-tr 1000.0 1000.0 {tmpfn}_nn.png {tmpfn}_nn.tif"
        )
        subprocess.call(cmd, shell=True)

        # Insert into LDM
        pqstr = (
            f"pqinsert -i -p 'plot c {tstr} "
            f"gis/images/3857/mrms/p{hr}h.tif "
            f"GIS/mrms/p{hr}h_{tstr}.tif tif' {tmpfn}.tif"
        )
        subprocess.call(pqstr, shell=True)

        pqstr = (
            f"pqinsert -i -p 'plot c {tstr} "
            f"gis/images/3857/mrms/p{hr}h_nn.tif "
            f"GIS/mrms/p{hr}h_{tstr}.tif tif' {tmpfn}_nn.tif"
        )
        subprocess.call(pqstr, shell=True)

        with open(f"{tmpfn}.json", "w", encoding="utf8") as fh:
            json.dump({"meta": metadata}, fh)

        # Insert into LDM
        pqstr = (
            f"pqinsert -i -p 'plot c {tstr} "
            f"gis/images/4326/mrms/p{hr}h.json "
            f"GIS/mrms/p{hr}h_{tstr}.json json' {tmpfn}.json"
        )
        subprocess.call(pqstr, shell=True)

        pqstr = (
            f"pqinsert -i -p 'plot c {tstr} "
            f"gis/images/4326/mrms/p{hr}h_nn.json "
            f"GIS/mrms/p{hr}h_{tstr}.json json' {tmpfn}.json"
        )
        subprocess.call(pqstr, shell=True)
    for suffix in ["tif", "json", "png", "wld"]:
        fn = f"{tmpfn}.{suffix}"
        if os.path.isfile(fn):
            os.unlink(fn)
    if irealtime:
        for suffix in ["tif", "png", "wld"]:
            fn = f"{tmpfn}_nn.{suffix}"
            if os.path.isfile(fn):
                os.unlink(fn)

    os.close(tmpfp)
    os.unlink(tmpfn)


def main(argv):
    """We are always explicitly called"""
    gts = datetime.datetime(
        int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4])
    )
    for hr in [1, 24, 48, 72]:
        doit(gts, hr)
        # Also reprocess last hour and six hours ago
        for offset in [1, 6]:
            doit(gts - datetime.timedelta(hours=offset), hr)
    cleanup()


if __name__ == "__main__":
    main(sys.argv)
