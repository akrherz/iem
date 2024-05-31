"""NEXRAD max reflectivity summary images.

Run from RUN_0Z.sh, RUN_10_AFTER.sh (6z)
"""

import datetime
import subprocess
import tempfile
import time

import click
import numpy as np
import requests
from osgeo import gdal, gdalconst
from pyiem.database import get_dbconn
from pyiem.util import archive_fetch, logger, utc

gdal.UseExceptions()
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


def run(tmpdir, prod, sts):
    """Create a max dbZ plot

    Args:
      prod (str): Product to run for, either n0r or n0q
      sts (datetime): date to run for
    """
    yest = utc() - datetime.timedelta(days=1)
    routes = "ac" if sts.date() == yest.date() else "a"
    label = f"{sts.hour}z{sts.hour}z"
    LOG.info("Running for %s with routes=%s, label=%s", sts, routes, label)
    ets = sts + datetime.timedelta(days=1)
    interval = datetime.timedelta(minutes=5)

    n0rct = get_colortable(prod)

    # Loop over our archived files and do what is necessary
    maxn0r = None
    now = sts
    while now < ets:
        ppath = now.strftime(f"%Y/%m/%d/GIS/uscomp/{prod}_%Y%m%d%H%M.png")
        with archive_fetch(ppath) as fn:
            if fn is None:
                LOG.warning("missing file: %s", ppath)
                now += interval
                continue
            n0r = gdal.Open(fn, 0)
            n0rd = n0r.ReadAsArray()
        LOG.info(
            "%s %s %s %s", now, n0rd.dtype, np.shape(n0rd), n0r.RasterCount
        )
        if maxn0r is None:
            maxn0r = n0rd
        maxn0r = np.where(n0rd > maxn0r, n0rd, maxn0r)

        now += interval

    out_driver = gdal.GetDriverByName("gtiff")
    outdataset = out_driver.Create(
        f"{tmpdir}/{sts:%Y%m%d%H}.tiff",
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
        [
            "magick",
            f"{tmpdir}/{sts:%Y%m%d%H}.tiff",
            f"{tmpdir}/{sts:%Y%m%d%H}.png",
        ],
    )
    # Insert into LDM
    cmd = [
        "pqinsert",
        "-p",
        f"plot a {sts:%Y%m%d%H}00 bogus "
        f"GIS/uscomp/max_{prod}_{label}_{sts:%Y%m%d}.png png",
        f"{tmpdir}/{sts:%Y%m%d%H}.png",
    ]
    LOG.info(" ".join(cmd))
    subprocess.call(cmd)

    # Create tmp world file
    wldfn = f"{tmpdir}/tmpwld{sts:%Y%m%d%H}.wld"
    with open(wldfn, "w", encoding="utf-8") as fh:
        if prod == "n0r":
            fh.write("0.01\n0.0\n0.0\n-0.01\n-126.0\n50.0")
        else:
            fh.write("0.005\n0.0\n0.0\n-0.005\n-126.0\n50.0")

    # Insert world file as well
    cmd = [
        "pqinsert",
        "-i",
        "-p",
        (
            f"plot a {sts:%Y%m%d%H}00 bogus "
            f"GIS/uscomp/max_{prod}_{label}_{sts:%Y%m%d}.wld wld"
        ),
        wldfn,
    ]
    LOG.info(" ".join(cmd))
    subprocess.call(cmd)

    # 60s was too tight it appears
    LOG.info("sleeping 180s to allow LDM to propogate")
    time.sleep(180)

    # Iowa
    layer = "nexrad_tc" if prod == "n0r" else "n0q_tc"
    if sts.hour == 6:
        layer = f"{layer}6"
    png = requests.get(
        f"{URLBASE}layers[]=uscounties&layers[]={layer}&ts={sts:%Y%m%d%H%M}",
        timeout=120,
    )
    with open(f"{tmpdir}/{sts:%Y%m%d%H}.png", "wb") as fh:
        fh.write(png.content)
    cmd = [
        "pqinsert",
        "-p",
        (
            f"plot {routes} {sts:%Y%m%d%H}00 "
            f"summary/max_{prod}_{label}_comprad.png "
            f"comprad/max_{prod}_{label}_{sts:%Y%m%d}.png png"
        ),
        f"{tmpdir}/{sts:%Y%m%d%H}.png",
    ]
    LOG.info(" ".join(cmd))
    subprocess.call(cmd)

    # US
    url = f"{URLBASE}sector=conus&layers[]={layer}&ts={sts:%Y%m%d%H%M}"
    png = requests.get(url, timeout=120)
    if png.status_code != 200:
        LOG.warning("Got status_code %s for %s", png.status_code, url)
    else:
        with open(f"{tmpdir}/{sts:%Y%m%d%H}.png", "wb") as fh:
            fh.write(png.content)
        cmd = [
            "pqinsert",
            "-p",
            (
                f"plot {routes} {sts:%Y%m%d%H}00 "
                f"summary/max_{prod}_{label}_usrad.png "
                f"usrad/max_{prod}_{label}_{sts:%Y%m%d}.png png"
            ),
            f"{tmpdir}/{sts:%Y%m%d%H}.png",
        ]
        LOG.info(" ".join(cmd))
        subprocess.call(cmd)


@click.command()
@click.option(
    "--valid", type=click.DateTime(), help="UTC Valid Time", required=True
)
def main(valid):
    """Run main()"""
    valid = valid.replace(tzinfo=datetime.timezone.utc)
    for prod in ["n0r", "n0q"]:
        if valid < utc(2010, 11, 13) and prod == "n0q":
            continue
        with tempfile.TemporaryDirectory() as tmpdir:
            run(tmpdir, prod, valid)


if __name__ == "__main__":
    main()
