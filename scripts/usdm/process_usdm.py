"""IEM Processing of the USDM Shapefiles"""

import datetime
import glob
import os
import subprocess
import sys
import tempfile
import zipfile

import fiona
import requests
from pyiem.database import get_dbconnc
from pyiem.util import exponential_backoff, logger
from shapely.geometry import MultiPolygon, shape

LOG = logger()
BASEURL = "https://droughtmonitor.unl.edu/data/shapefiles_m/"


def database_save(date, shpfn):
    """Save to our databasem please"""
    pgconn, cursor = get_dbconnc("postgis")
    cursor.execute("DELETE from usdm where valid = %s", (date,))
    if cursor.rowcount > 0:
        LOG.info("    database delete removed %s rows", cursor.rowcount)
    with fiona.open(shpfn) as shps:
        for shp in shps:
            geo = shape(shp["geometry"])
            if geo.geom_type == "Polygon":
                geo = MultiPolygon([geo])
            cursor.execute(
                "INSERT into usdm(valid, dm, geom) VALUES "
                "(%s, %s, st_setsrid(st_geomfromtext(%s), 4326))",
                (date, shp["properties"]["DM"], geo.wkt),
            )
    cursor.close()
    pgconn.commit()
    pgconn.close()


def workflow(date, routes):
    """Do work for this date"""
    # print("process_usdm workflow for %s" % (date, ))
    # 1. get file from USDM website
    url = f"{BASEURL}USDM_{date:%Y%m%d}_M.zip"
    LOG.info("Fetching %s", url)
    req = exponential_backoff(requests.get, url, timeout=30)
    if req is None:
        LOG.info("Download full fail: %s", url)
        return
    if req.status_code != 200:
        LOG.info("Download failed for: %s code: %s", url, req.status_code)
        return
    tmp = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
    tmp.write(req.content)
    tmp.close()
    zipfp = zipfile.ZipFile(tmp.name, "r")
    shpfn = None
    for name in zipfp.namelist():
        with open(f"/tmp/{name}", "wb") as fp:
            fp.write(zipfp.read(name))
        if name[-3:] == "shp":
            shpfn = f"/tmp/{name}"
    # 2. Save it to the database
    database_save(date, shpfn)
    # 3. Send it to LDM for current and archive writing
    for fn in glob.glob(f"/tmp/USDM_{date:%Y%m%d}*"):
        suffix = fn.split("/")[-1].split(".", 1)[1]
        cmd = [
            "pqinsert",
            "-i",
            "-p",
            f"data {routes} {date:%Y%m%d}0000 "
            f"gis/shape/4326/us/dm_current.{suffix} "
            f"GIS/usdm/{fn.split('/')[-1]} bogus",
            fn,
        ]
        LOG.info(" ".join(cmd))
        subprocess.call(cmd)
        os.unlink(fn)
    # 4. Clean up after ourself
    os.unlink(tmp.name)


def main(argv):
    """Go Main Go"""
    if len(argv) == 1:
        # Run for most recent Tuesday
        today = datetime.date.today()
        routes = "ac"
    else:
        today = datetime.date(int(argv[1]), int(argv[2]), int(argv[3]))
        routes = "a"
    offset = (today.weekday() - 1) % 7
    tuesday = today - datetime.timedelta(days=offset)
    workflow(tuesday, routes)


if __name__ == "__main__":
    main(sys.argv)
