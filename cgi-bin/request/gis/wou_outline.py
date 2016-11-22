#!/usr/bin/env python
""" Generate a Watch Outline for a given SPC convective watch """

import shapelib
import dbflib
import zipfile
import os
import shutil
import sys
import cgi
from pyiem import wellknowntext
import psycopg2.extras
POSTGIS = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
pcursor = POSTGIS.cursor(cursor_factory=psycopg2.extras.DictCursor)

pcursor.execute("SET TIME ZONE 'GMT'")

# Get CGI vars
form = cgi.FormContent()
year = int(form["year"][0])
etn = int(form["etn"][0])
fp = "watch_%s_%s" % (year, etn)

os.chdir("/tmp/")

shp = shapelib.create(fp, shapelib.SHPT_POLYGON)

dbf = dbflib.create(fp)
dbf.add_field("SIG", dbflib.FTString, 1, 0)
dbf.add_field("ETN", dbflib.FTInteger, 4, 0)

sql = """select
    ST_astext(ST_multi(ST_union(ST_SnapToGrid(u.geom,0.0001)))) as tgeom
    from warnings_%s w JOIN ugcs u on (u.gid = w.gid) WHERE significance = 'A'
    and phenomena IN ('TO','SV') and eventid = %s and
    ST_isvalid(u.geom) and issue < ((select issued from watches WHERE num = %s
        and extract(year from issued) = %s LIMIT 1) + '60 minutes'::interval)
""" % (year, etn, etn, year)
pcursor.execute(sql)

if pcursor.rowcount == 0:
    sys.exit()

row = pcursor.fetchone()
s = row["tgeom"]
f = wellknowntext.convert_well_known_text(s)

d = {}
d["SIG"] = 'A'
d["ETN"] = etn

obj = shapelib.SHPObject(shapelib.SHPT_POLYGON, 1, f)
shp.write_object(-1, obj)
dbf.write_record(0, d)
del(obj)

del(shp)
del(dbf)

# Create zip file, send it back to the clients
shutil.copyfile("/opt/iem/data/gis/meta/4326.prj",
                fp+".prj")
z = zipfile.ZipFile(fp+".zip", 'w', zipfile.ZIP_DEFLATED)
z.write(fp+".shp")
z.write(fp+".shx")
z.write(fp+".dbf")
z.write(fp+".prj")
z.close()

sys.stdout.write("Content-type: application/octet-stream\n")
sys.stdout.write("Content-Disposition: attachment; filename=%s.zip\n" % (fp,))

sys.stdout.write(file(fp+".zip", 'r').read())

os.remove(fp+".zip")
os.remove(fp+".shp")
os.remove(fp+".shx")
os.remove(fp+".dbf")
os.remove(fp+".prj")
