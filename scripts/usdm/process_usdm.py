"""IEM Processing of the USDM Shapefiles"""
from __future__ import print_function
import sys
import datetime
import tempfile
import zipfile
import os
import subprocess
import glob

import requests
import fiona
from shapely.geometry import shape, MultiPolygon
from pyiem.util import get_dbconn, exponential_backoff

BASEURL = "https://droughtmonitor.unl.edu/data/shapefiles_m/"
PQINSERT = "/home/ldm/bin/pqinsert"


def database_save(date, shpfn):
    """Save to our databasem please"""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    cursor.execute("""DELETE from usdm where valid = %s""", (date,))
    if cursor.rowcount > 0:
        print("    database delete removed %s rows" % (cursor.rowcount,))
    with fiona.open(shpfn) as shps:
        for shp in shps:
            geo = shape(shp["geometry"])
            if geo.type == "Polygon":
                geo = MultiPolygon([geo])
            cursor.execute(
                """
                INSERT into usdm(valid, dm, geom) VALUES
                (%s, %s, st_setsrid(st_geomfromtext(%s), 4326))
            """,
                (date, shp["properties"]["DM"], geo.wkt),
            )
    cursor.close()
    pgconn.commit()


def workflow(date, routes):
    """Do work for this date"""
    # print("process_usdm workflow for %s" % (date, ))
    # 1. get file from USDM website
    url = "%sUSDM_%s_M.zip" % (BASEURL, date.strftime("%Y%m%d"))
    req = exponential_backoff(requests.get, url, timeout=30)
    if req is None:
        print("process_usdm download full fail: %s" % (url,))
        return
    if req.status_code != 200:
        print(
            ("process_usdm download failed for: %s code: %s")
            % (url, req.status_code)
        )
        return
    tmp = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
    tmp.write(req.content)
    tmp.close()
    zipfp = zipfile.ZipFile(tmp.name, "r")
    shpfn = None
    for name in zipfp.namelist():
        # print("    extracting: %s" % (name, ))
        fp = open("/tmp/%s" % (name,), "wb")
        fp.write(zipfp.read(name))
        fp.close()
        if name[-3:] == "shp":
            shpfn = "/tmp/" + name
    # 2. Save it to the database
    database_save(date, shpfn)
    # 3. Send it to LDM for current and archive writing
    for fn in glob.glob("/tmp/USDM_%s*" % (date.strftime("%Y%m%d"),)):
        suffix = fn.split("/")[-1].split(".", 1)[1]
        cmd = (
            "%s -i -p 'data %s %s0000 gis/shape/4326/us/dm_current.%s "
            "GIS/usdm/%s bogus' %s"
        ) % (
            PQINSERT,
            routes,
            date.strftime("%Y%m%d"),
            suffix,
            fn.split("/")[-1],
            fn,
        )
        subprocess.call(cmd, shell=True)
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
