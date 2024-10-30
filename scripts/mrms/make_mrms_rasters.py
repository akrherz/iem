"""
Generate a raster of XXhour precipitation totals from MRMS

run from RUN_10_AFTER.sh

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
from PIL import Image
from pyiem import mrms
from pyiem.reference import ISO8601
from pyiem.util import archive_fetch, logger

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
    utcnow = datetime.utcnow()
    return utcnow.strftime("%Y%m%d%H") == gts.strftime("%Y%m%d%H")


def need_not_run(gts, hr) -> bool:
    """Do we need to run for this combination?"""
    with archive_fetch(
        f"{gts:%Y/%m/%d}/GIS/mrms/p{hr}h_{gts:%Y%m%d%H%M}.png"
    ) as fh:
        if fh is None:
            return False
    return True


def doit(gts: datetime, hr: int):
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
    sts = gts - timedelta(hours=hr)
    times = [gts]
    if hr > 24:
        times.append(gts - timedelta(hours=24))
    if hr == 72:
        times.append(gts - timedelta(hours=48))
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
        with (
            gzip.GzipFile(gribfn, "rb") as fp,
            tempfile.NamedTemporaryFile(delete=False) as tmpfp,
        ):
            tmpfp.write(fp.read())
        grbs = pygrib.open(tmpfp.name)
        grb = grbs[1]
        grbs.close()
        os.unlink(tmpfp.name)

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
    cmd = [
        "pqinsert",
        "-i",
        "-p",
        f"plot {routes} {tstr} gis/images/4326/mrms/p{hr}h.wld "
        f"GIS/mrms/p{hr}h_{tstr}.wld wld",
        f"{tmpfn}.wld",
    ]
    subprocess.call(cmd)

    if irealtime:
        cmd = [
            "pqinsert",
            "-i",
            "-p",
            f"plot c {tstr} gis/images/4326/mrms/p{hr}h_nn.wld "
            f"GIS/mrms/p{hr}h_{tstr}.wld wld",
            f"{tmpfn}_nn.wld",
        ]
        subprocess.call(cmd)

    # Now we inject into LDM
    cmd = [
        "pqinsert",
        "-i",
        "-p",
        f"plot {routes} {tstr} gis/images/4326/mrms/p{hr}h.png "
        f"GIS/mrms/p{hr}h_{tstr}.png png",
        f"{tmpfn}.png",
    ]
    subprocess.call(cmd)

    if irealtime:
        # Now we inject into LDM
        cmd = [
            "pqinsert",
            "-i",
            "-p",
            f"plot c {tstr} gis/images/4326/mrms/p{hr}h_nn.png "
            f"GIS/mrms/p{hr}h_{tstr}.png png",
            f"{tmpfn}_nn.png",
        ]
        subprocess.call(cmd)

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
            f"{tmpfn}_nn.png",
            f"{tmpfn}_nn.tif",
        ]
        subprocess.call(cmd)

        # Insert into LDM
        cmd = [
            "pqinsert",
            "-i",
            "-p",
            f"plot c {tstr} gis/images/3857/mrms/p{hr}h.tif "
            f"GIS/mrms/p{hr}h_{tstr}.tif tif",
            f"{tmpfn}.tif",
        ]
        subprocess.call(cmd)

        cmd = [
            "pqinsert",
            "-i",
            "-p",
            f"plot c {tstr} gis/images/3857/mrms/p{hr}h_nn.tif "
            f"GIS/mrms/p{hr}h_{tstr}.tif tif",
            f"{tmpfn}_nn.tif",
        ]
        subprocess.call(cmd)

        with open(f"{tmpfn}.json", "w", encoding="utf8") as fh:
            json.dump({"meta": metadata}, fh)

        # Insert into LDM
        cmd = [
            "pqinsert",
            "-i",
            "-p",
            f"plot c {tstr} gis/images/4326/mrms/p{hr}h.json "
            f"GIS/mrms/p{hr}h_{tstr}.json json",
            f"{tmpfn}.json",
        ]
        subprocess.call(cmd)

        cmd = [
            "pqinsert",
            "-i",
            "-p",
            f"plot c {tstr} gis/images/4326/mrms/p{hr}h_nn.json "
            f"GIS/mrms/p{hr}h_{tstr}.json json",
            f"{tmpfn}.json",
        ]
        subprocess.call(cmd)
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


@click.command()
@click.option("--valid", type=click.DateTime(), required=True)
def main(valid: datetime):
    """We are always explicitly called"""
    valid = valid.replace(tzinfo=timezone.utc)
    for hr in [1, 24, 48, 72]:
        doit(valid, hr)
        # Also reprocess last hour and six hours ago
        for offset in [1, 6]:
            doit(valid - timedelta(hours=offset), hr)
    cleanup()


if __name__ == "__main__":
    main()
