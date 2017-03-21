"""Dump 24 hour LSRs to a file"""

import shapefile
import mx.DateTime
import zipfile
import os
import shutil
from pyiem import wellknowntext
import subprocess
import psycopg2.extras
POSTGIS = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
pcursor = POSTGIS.cursor(cursor_factory=psycopg2.extras.DictCursor)
pcursor.execute("SET TIME ZONE 'UTC'")

os.chdir("/tmp/")

# We set one minute into the future, so to get expiring warnings
# out of the shapefile
eTS = mx.DateTime.gmt() + mx.DateTime.RelativeDateTime(minutes=+1)

w = shapefile.Writer(shapefile.POINT)
w.field("VALID", 'C', 12, 0)
w.field("MAG", 'D', 10, 2)
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
    """ % (eTS.year,))

cnt = 0
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
             row['remark'][:200]
             )
w.save("lsr_24hour.shp")
z = zipfile.ZipFile("lsr_24hour.zip", 'w', zipfile.ZIP_DEFLATED)
z.write("lsr_24hour.shp")
z.write("lsr_24hour.shx")
z.write("lsr_24hour.dbf")
shutil.copy('/opt/iem/data/gis/meta/4326.prj', 'lsr_24hour.prj')
z.write("lsr_24hour.prj")
z.close()

cmd = ("/home/ldm/bin/pqinsert -p \"zip c %s gis/shape/4326/us/lsr_24hour.zip "
       "bogus zip\" lsr_24hour.zip") % (eTS.strftime("%Y%m%d%H%M"),)
subprocess.call(cmd, shell=True)

for suffix in ['shp', 'shx', 'dbf', 'prj', 'zip']:
    os.remove('lsr_24hour.%s' % (suffix,))
