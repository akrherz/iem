""" 
Something to dump current warnings to a shapefile
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
if POSTGIS is None: 
	sys.exit(0)
pcursor = POSTGIS.cursor(cursor_factory=psycopg2.extras.DictCursor)
pcursor.execute("SET TIME ZONE 'GMT'")
# Don't print out annonying errors about ST_IsValid failures
pcursor.execute("set client_min_messages = ERROR")

os.chdir("/tmp")

# We set one minute into the future, so to get expiring warnings
# out of the shapefile
eTS = mx.DateTime.gmt() + mx.DateTime.RelativeDateTime(minutes=+1)

shp = shapelib.create("current_ww", shapelib.SHPT_POLYGON)

dbf = dbflib.create("current_ww")
dbf.add_field("ISSUED", dbflib.FTString, 12, 0)
dbf.add_field("EXPIRED", dbflib.FTString, 12, 0)
dbf.add_field("UPDATED", dbflib.FTString, 12, 0)
dbf.add_field("TYPE", dbflib.FTString, 2, 0)
dbf.add_field("GTYPE", dbflib.FTString, 1, 0)
dbf.add_field("SIG", dbflib.FTString, 1, 0)
dbf.add_field("WFO", dbflib.FTString, 3, 0)
dbf.add_field("ETN", dbflib.FTInteger, 4, 0)
dbf.add_field("STATUS", dbflib.FTString, 3, 0)
dbf.add_field("NWS_UGC", dbflib.FTString, 6, 0)


sql = """SELECT *, astext(ST_Simplify(geom,0.001)) as tgeom from warnings_%s 
	WHERE expire > '%s' and ((gtype = 'P' and ST_IsValid(geom)) or gtype = 'C') 
	ORDER by type ASC""" % (eTS.year, eTS.strftime("%Y-%m-%d %H:%M"),)
pcursor.execute(sql)

cnt = 0
for row in pcursor:
	s = row["tgeom"]
	if s is None or s == "":
		continue
	    #print rs[i]['phenomena'], rs[i]['eventid'], rs[i]['wfo'], rs[i]['ugc']
	try:
		f = wellknowntext.convert_well_known_text(s)
	except:
		continue
	
	g = row["gtype"]
	t = row["phenomena"]
	d = {}
	d["ISSUED"] = row['issue'].strftime("%Y%m%d%H%M")
	d["EXPIRED"] = row['expire'].strftime("%Y%m%d%H%M")
	d["UPDATED"] = row['updated'].strftime("%Y%m%d%H%M")
	d["TYPE"] = t
	d["GTYPE"] = g
	d["SIG"] = row["significance"]
	d["WFO"] = row["wfo"]
	d["STATUS"] = row["status"]
	d["ETN"] = row["eventid"]
	d["NWS_UGC"] = row["ugc"]
	
	obj = shapelib.SHPObject(shapelib.SHPT_POLYGON, 1, f )
	shp.write_object(-1, obj)
	dbf.write_record(cnt, d)
	del(obj)
	cnt += 1

if (cnt == 0):
	obj = shapelib.SHPObject(shapelib.SHPT_POLYGON, 1, [[(0.1, 0.1), 
									(0.2, 0.2), (0.3, 0.1), (0.1, 0.1)]])
	d = {}
	d["ISSUED"] = "200000000000"
	d["EXPIRED"] = "200000000000"
	d["UPDATED"] = "200000000000"
	d["TYPE"] = "ZZ"
	d["GTYPE"] = "Z"
	shp.write_object(-1, obj)
	dbf.write_record(0, d)

del(shp)
del(dbf)
z = zipfile.ZipFile("current_ww.zip", 'w', zipfile.ZIP_DEFLATED)
z.write("current_ww.shp")
shutil.copy('/mesonet/www/apps/iemwebsite/scripts/GIS/current_ww.shp.xml', 'current_ww.shp.xml')
z.write("current_ww.shp.xml")
z.write("current_ww.shx")
z.write("current_ww.dbf")
shutil.copy('/mesonet/data/gis/meta/4326.prj', 'current_ww.prj')
z.write("current_ww.prj")
z.close()

cmd = "/home/ldm/bin/pqinsert -p \"zip c %s gis/shape/4326/us/current_ww.zip bogus zip\" current_ww.zip" % (eTS.strftime("%Y%m%d%H%M"),)
subprocess.call(cmd, shell=True)
for suffix in ['shp', 'shp.xml', 'shx', 'dbf', 'prj', 'zip']:
	os.remove('current_ww.%s' % (suffix,))
