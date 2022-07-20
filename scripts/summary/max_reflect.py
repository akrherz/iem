"""NEXRAD max reflectivity summary images.

Run from RUN_0Z.sh, RUN_10_AFTER.sh (6z)
"""
import datetime
import os
import time
import sys
import subprocess

import requests
from osgeo import gdal, gdalconst
import numpy as np
from pyiem.util import get_dbconn, logger, utc

LOG = logger()
URLBASE = "http://iem.local/GIS/radmap.php?width=1280&height=720&"


def get_colortable(prod):
    """Get the color table for this prod

    Args:
      prod (str): product to get the table for

    Returns:
      colortable

    """
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    cursor.execute(
        "select r,g,b from iemrasters_lookup l JOIN iemrasters r on "
        "(r.id = l.iemraster_id) WHERE r.name = %s ORDER by l.coloridx ASC",
        ("composite_" + prod,),
    )
    ct = gdal.ColorTable()
    for i, row in enumerate(cursor):
        ct.SetColorEntry(i, (row[0], row[1], row[2], 255))
    pgconn.close()
    return ct


def run(prod, sts):
    """Create a max dbZ plot

    Args:
      prod (str): Product to run for, either n0r or n0q
      sts (datetime): date to run for
    """
    yest = utc() - datetime.timedelta(days=1)
    routes = "ac" if sts.date() == yest.date() else "c"
    label = f"{sts.hour}z{sts.hour}z"
    LOG.info("Running for %s with routes=%s, label=%s", sts, routes, label)
    ets = sts + datetime.timedelta(days=1)
    interval = datetime.timedelta(minutes=5)

    n0rct = get_colortable(prod)

    # Loop over our archived files and do what is necessary
    maxn0r = None
    now = sts
    while now < ets:
        fn = now.strftime(
            f"/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/uscomp/{prod}_%Y%m%d%H%M.png"
        )
        if not os.path.isfile(fn):
            LOG.warning("missing file: %s", fn)
            now += interval
            continue
        n0r = gdal.Open(fn, 0)
        n0rd = n0r.ReadAsArray()
        LOG.debug(
            "%s %s %s %s", now, n0rd.dtype, np.shape(n0rd), n0r.RasterCount
        )
        if maxn0r is None:
            maxn0r = n0rd
        maxn0r = np.where(n0rd > maxn0r, n0rd, maxn0r)

        now += interval

    out_driver = gdal.GetDriverByName("gtiff")
    outdataset = out_driver.Create(
        f"/tmp/{sts:%Y%m%d%H}.tiff",
        n0r.RasterXSize,
        n0r.RasterYSize,
        n0r.RasterCount,
        gdalconst.GDT_Byte,
    )
    # Set output color table to match input
    outdataset.GetRasterBand(1).SetRasterColorTable(n0rct)
    outdataset.GetRasterBand(1).WriteArray(maxn0r)
    del outdataset

    subprocess.call(
        f"convert /tmp/{sts:%Y%m%d%H}.tiff /tmp/{sts:%Y%m%d%H}.png",
        shell=True,
    )
    # Insert into LDM
    cmd = (
        f"pqinsert -p 'plot a {sts:%Y%m%d%H}00 bogus "
        f"GIS/uscomp/max_{prod}_{label}_{sts:%Y%m%d}.png png' "
        f"/tmp/{sts:%Y%m%d%H}.png"
    )
    LOG.info(cmd)
    subprocess.call(cmd, shell=True)

    # Create tmp world file
    wldfn = f"/tmp/tmpwld{sts:%Y%m%d%H}.wld"
    with open(wldfn, "w", encoding="utf-8") as fh:
        if prod == "n0r":
            fh.write("0.01\n0.0\n0.0\n-0.01\n-126.0\n50.0")
        else:
            fh.write("0.005\n0.0\n0.0\n-0.005\n-126.0\n50.0")

    # Insert world file as well
    cmd = (
        f"pqinsert -i -p 'plot a {sts:%Y%m%d%H}00 bogus "
        f"GIS/uscomp/max_{prod}_{label}_{sts:%Y%m%d}.wld wld' {wldfn}"
    )
    LOG.info(cmd)
    subprocess.call(cmd, shell=True)

    # cleanup
    os.remove(f"/tmp/{sts:%Y%m%d%H}.tiff")
    os.remove(f"/tmp/{sts:%Y%m%d%H}.png")
    os.remove(wldfn)

    LOG.info("sleeping 60 to allow LDM to propogate")
    time.sleep(60)

    # Iowa
    layer = "nexrad_tc" if prod == "n0r" else "n0q_tc"
    if sts.hour == 6:
        layer = f"{layer}6"
    png = requests.get(
        f"{URLBASE}layers[]=uscounties&layers[]={layer}&ts={sts:%Y%m%d%H%M}"
    )
    with open(f"/tmp/{sts:%Y%m%d%H}.png", "wb") as fh:
        fh.write(png.content)
    cmd = (
        f"pqinsert -p 'plot {routes} {sts:%Y%m%d%H}00 "
        f"summary/max_{prod}_{label}_comprad.png "
        f"comprad/max_{prod}_{label}_{sts:%Y%m%d}.png png' "
        f"/tmp/{sts:%Y%m%d%H}.png"
    )
    LOG.info(cmd)
    subprocess.call(cmd, shell=True)

    # US
    png = requests.get(
        f"{URLBASE}sector=conus&layers[]=uscounties&layers[]={layer}"
        f"&ts={sts:%Y%m%d%H%M}"
    )
    with open(f"/tmp/{sts:%Y%m%d%H}.png", "wb") as fh:
        fh.write(png.content)
    cmd = (
        f"pqinsert -p 'plot {routes} {sts:%Y%m%d%H}00 "
        f"summary/max_{prod}_{label}_usrad.png "
        f"usrad/max_{prod}_{label}_{sts:%Y%m%d}.png png' "
        f"/tmp/{sts:%Y%m%d%H}.png"
    )
    LOG.info(cmd)
    subprocess.call(cmd, shell=True)
    os.remove(f"/tmp/{sts:%Y%m%d%H}.png")


def main(argv):
    """Run main()"""
    ts = utc(*[int(i) for i in argv[1:5]])
    for prod in ["n0r", "n0q"]:
        run(prod, ts)


if __name__ == "__main__":
    main(sys.argv)
