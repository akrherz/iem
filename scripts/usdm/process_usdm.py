"""IEM Processing of the USDM Shapefiles.

Called from dedicated crontab
"""

import glob
import os
import subprocess
import tempfile
import zipfile
from datetime import date, datetime, timedelta
from typing import Optional

import click
import fiona
import httpx
from pyiem.database import get_dbconnc
from pyiem.util import exponential_backoff, logger
from shapely.geometry import MultiPolygon, shape

LOG = logger()
BASEURL = "https://droughtmonitor.unl.edu/data/shapefiles_m/"


def database_save(dt: date, shpfn):
    """Save to our databasem please"""
    pgconn, cursor = get_dbconnc("postgis")
    cursor.execute("DELETE from usdm where valid = %s", (dt,))
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


def workflow(dt: date, routes):
    """Do work for this date"""
    # 1. get file from USDM website
    url = f"{BASEURL}USDM_{dt:%Y%m%d}_M.zip"
    LOG.info("Fetching %s", url)
    req = exponential_backoff(httpx.get, url, timeout=30)
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
    database_save(dt, shpfn)
    # 3. Send it to LDM for current and archive writing
    for fn in glob.glob(f"/tmp/USDM_{dt:%Y%m%d}*"):
        suffix = fn.split("/")[-1].split(".", 1)[1]
        cmd = [
            "pqinsert",
            "-i",
            "-p",
            f"data {routes} {dt:%Y%m%d}0000 "
            f"gis/shape/4326/us/dm_current.{suffix} "
            f"GIS/usdm/{fn.split('/')[-1]} bogus",
            fn,
        ]
        LOG.info(" ".join(cmd))
        subprocess.call(cmd)
        os.unlink(fn)
    # 4. Clean up after ourself
    os.unlink(tmp.name)


@click.command()
@click.option("--date", "dt", type=click.DateTime(), help="Specific date")
def main(dt: Optional[datetime]):
    """Go Main Go"""
    if dt is None:
        # Run for most recent Tuesday
        today = date.today()
        routes = "ac"
    else:
        today = dt.date()
        routes = "a"
    offset = (today.weekday() - 1) % 7
    tuesday = today - timedelta(days=offset)
    workflow(tuesday, routes)


if __name__ == "__main__":
    main()
