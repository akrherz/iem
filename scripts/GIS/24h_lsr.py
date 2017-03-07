"""
 Dump 24 hour LSRs to a file
"""

import shapelib
import dbflib
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

shp = shapelib.create("lsr_24hour", shapelib.SHPT_POINT)

dbf = dbflib.create("lsr_24hour")
dbf.add_field("VALID", dbflib.FTString, 12, 0)
dbf.add_field("MAG", dbflib.FTDouble, 10, 2)
dbf.add_field("WFO", dbflib.FTString, 3, 0)
dbf.add_field("TYPECODE", dbflib.FTString, 1, 0)
dbf.add_field("TYPETEXT", dbflib.FTString, 40, 0)
dbf.add_field("CITY", dbflib.FTString, 40, 0)
dbf.add_field("COUNTY", dbflib.FTString, 40, 0)
dbf.add_field("SOURCE", dbflib.FTString, 40, 0)
dbf.add_field("REMARK", dbflib.FTString, 200, 0)


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

    d = {}
    d["VALID"] = row['valid'].strftime("%Y%m%d%H%M")
    d["MAG"] = float(row['magnitude'] or 0)
    d["TYPECODE"] = row['type']
    d["WFO"] = row['wfo']
    d["TYPETEXT"] = row['typetext']
    d["CITY"] = row['city']
    d["COUNTY"] = row['county']
    d["SOURCE"] = row['source']
    d["REMARK"] = row['remark'][:200]
    obj = shapelib.SHPObject(shapelib.SHPT_POINT, 1, [[f]])
    shp.write_object(-1, obj)
    dbf.write_record(cnt, d)
    del(obj)
    cnt += 1


del(shp)
del(dbf)
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
