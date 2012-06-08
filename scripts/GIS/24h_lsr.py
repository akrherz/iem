"""
 Dump 24 hour LSRs to a file
"""

import shapelib
import dbflib
import mx.DateTime
import zipfile
import os
import sys
import shutil
import wellknowntext
import iemdb
import subprocess
import psycopg2.extras
POSTGIS = iemdb.connect('postgis', bypass=True)
pcursor = POSTGIS.cursor(cursor_factory=psycopg2.extras.DictCursor)
pcursor.execute("SET TIME ZONE 'GMT'")

os.chdir("/tmp/")

"""
 valid     | timestamp with time zone |
 type      | character(1)             |
 magnitude | real                     |
 city      | character varying(32)    |
 county    | character varying(32)    |
 state     | character(2)             |
 source    | character varying(32)    |
 remark    | text                     |
 wfo       | character(3)             |
 geom      | geometry                 |
 typetext  | geometry                 |
"""

# We set one minute into the future, so to get expiring warnings
# out of the shapefile
eTS = mx.DateTime.gmt() + mx.DateTime.RelativeDateTime(minutes=+1)

shp = shapelib.create("lsr_24hour", shapelib.SHPT_POINT)

dbf = dbflib.create("lsr_24hour")
dbf.add_field("VALID", dbflib.FTString, 12, 0)
dbf.add_field("MAG", dbflib.FTDouble, 8, 2)
dbf.add_field("WFO", dbflib.FTString, 3, 0)
dbf.add_field("TYPECODE", dbflib.FTString, 1, 0)
dbf.add_field("TYPETEXT", dbflib.FTString, 40, 0)
dbf.add_field("CITY", dbflib.FTString, 40, 0)
dbf.add_field("COUNTY", dbflib.FTString, 40, 0)
dbf.add_field("SOURCE", dbflib.FTString, 40, 0)
dbf.add_field("REMARK", dbflib.FTString, 200, 0)


#sql = "SELECT *, astext(geom) as tgeom from warnings WHERE issue < '%s' and \
sql = """SELECT distinct *, astext(geom) as tgeom from lsrs_%s WHERE 
	valid > (now() -'1 day'::interval) """ % (eTS.year,)
pcursor.execute(sql)

cnt = 0
for row in pcursor:
	
	s = row["tgeom"]
	if s == None or s == "":
		continue
	f = wellknowntext.convert_well_known_text(s)

	d = {}
	d["VALID"] = row['valid'].strftime("%Y%m%d%H%M")
	d["MAG"] = float(row['magnitude'])
	d["TYPECODE"] = row['type']
	d["WFO"] = row['wfo']
	d["TYPETEXT"] = row['typetext']
	d["CITY"] = row['city']
	d["COUNTY"] = row['county']
	d["SOURCE"] = row['source']
	d["REMARK"] = row['remark'][:200]
	obj = shapelib.SHPObject(shapelib.SHPT_POINT, 1, [[f]] )
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
shutil.copy('/mesonet/data/gis/meta/4326.prj', 'lsr_24hour.prj')
z.write("lsr_24hour.prj")
z.close()

cmd = "/home/ldm/bin/pqinsert -p \"zip c %s gis/shape/4326/us/lsr_24hour.zip bogus zip\" lsr_24hour.zip" % (eTS.strftime("%Y%m%d%H%M"),)
subprocess.call(cmd, shell=True)

for suffix in ['shp', 'shx', 'dbf', 'prj', 'zip']:
	os.remove('lsr_24hour.%s' % (suffix,))
