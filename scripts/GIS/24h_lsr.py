"""Dump 24 hour LSRs to a file"""
import zipfile
import os
import shutil
import subprocess
import datetime

import shapefile
import psycopg2.extras
from pyiem import wellknowntext
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    pgconn = get_dbconn('postgis', user='nobody')
    pcursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    pcursor.execute("SET TIME ZONE 'UTC'")

    os.chdir("/tmp/")

    # We set one minute into the future, so to get expiring warnings
    # out of the shapefile
    ets = datetime.datetime.utcnow() + datetime.timedelta(minutes=+1)

    w = shapefile.Writer("lsr_24hour")
    w.field("VALID", 'C', 12, 0)
    w.field("MAG", 'F', 10, 2)
    w.field("WFO", 'C', 3, 0)
    w.field("TYPECODE", 'C', 1, 0)
    w.field("TYPETEXT", 'C', 40, 0)
    w.field("CITY", 'C', 40, 0)
    w.field("COUNTY", 'C', 40, 0)
    w.field("SOURCE", 'C', 40, 0)
    w.field("REMARK", 'C', 200, 0)

    pcursor.execute("""
        SELECT distinct *, ST_astext(geom) as tgeom from lsrs_%s WHERE
        valid > (now() -'1 day'::interval)
        """ % (ets.year,))

    for row in pcursor:
        s = row["tgeom"]
        if s is None or s == "":
            continue
        f = wellknowntext.convert_well_known_text(s)
        w.point(f[0], f[1])
        w.record(row['valid'].strftime("%Y%m%d%H%M"),
                 float(row['magnitude'] or 0),
                 row['wfo'],
                 row['type'],
                 row['typetext'],
                 row['city'],
                 row['county'],
                 row['source'],
                 row['remark'].encode(
                     'utf-8', 'ignore').decode('ascii', 'ignore')[:200]
                 )
    w.close()
    zfh = zipfile.ZipFile("lsr_24hour.zip", 'w', zipfile.ZIP_DEFLATED)
    zfh.write("lsr_24hour.shp")
    zfh.write("lsr_24hour.shx")
    zfh.write("lsr_24hour.dbf")
    shutil.copy('/opt/iem/data/gis/meta/4326.prj', 'lsr_24hour.prj')
    zfh.write("lsr_24hour.prj")
    zfh.close()

    cmd = ("/home/ldm/bin/pqinsert "
           "-p \"zip c %s gis/shape/4326/us/lsr_24hour.zip "
           "bogus zip\" lsr_24hour.zip") % (ets.strftime("%Y%m%d%H%M"),)
    subprocess.call(cmd, shell=True)

    for suffix in ['shp', 'shx', 'dbf', 'prj', 'zip']:
        os.remove('lsr_24hour.%s' % (suffix,))


if __name__ == '__main__':
    main()
