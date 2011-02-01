# Something to dump current warnings to a shapefile
# 28 Aug 2004 port to iem40

import shapelib, dbflib, mx.DateTime, zipfile, os, sys, shutil
from pyIEM import wellknowntext, iemdb
i = iemdb.iemdb()
mydb = i["postgis"]
if (mydb == None): 
	sys.exit(0)
mydb.query("SET TIME ZONE 'GMT'")

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


sql = "SELECT *, astext(geom) as tgeom from warnings_%s WHERE \
	expire > '%s' ORDER by type ASC" % (eTS.year, \
        eTS.strftime("%Y-%m-%d %H:%M"),)
#print sql
rs = mydb.query(sql).dictresult()

cnt = 0
for i in range(len(rs)):
	s = rs[i]["tgeom"]
	if (s == None or s == ""):
		continue
	f = wellknowntext.convert_well_known_text(s)

	g = rs[i]["gtype"]
	t = rs[i]["phenomena"]
	issue = mx.DateTime.strptime(rs[i]["issue"][:16], "%Y-%m-%d %H:%M")
	expire = mx.DateTime.strptime(rs[i]["expire"][:16],"%Y-%m-%d %H:%M")
	updated = mx.DateTime.strptime(rs[i]["updated"][:16],"%Y-%m-%d %H:%M")
	d = {}
	d["ISSUED"] = issue.strftime("%Y%m%d%H%M")
	d["EXPIRED"] = expire.strftime("%Y%m%d%H%M")
	d["UPDATED"] = updated.strftime("%Y%m%d%H%M")
	d["TYPE"] = t
	d["GTYPE"] = g
	d["SIG"] = rs[i]["significance"]
	d["WFO"] = rs[i]["wfo"]
	d["STATUS"] = rs[i]["status"]
	d["ETN"] = rs[i]["eventid"]

	obj = shapelib.SHPObject(shapelib.SHPT_POLYGON, 1, f )
	shp.write_object(-1, obj)
	dbf.write_record(cnt, d)
	del(obj)
	cnt += 1

if (cnt == 0):
	obj = shapelib.SHPObject(shapelib.SHPT_POLYGON, 1, [[(0.1, 0.1), (0.2, 0.2), (0.3, 0.1), (0.1, 0.1)]])
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
shutil.copy('/var/www/scripts/GIS/current_ww.shp.xml', 'current_ww.shp.xml')
z.write("current_ww.shp.xml")
z.write("current_ww.shx")
z.write("current_ww.dbf")
shutil.copy('/mesonet/data/gis/meta/4326.prj', 'current_ww.prj')
z.write("current_ww.prj")
z.close()

cmd = "/home/ldm/bin/pqinsert -p \"zip c %s gis/shape/4326/us/current_ww.zip bogus zip\" current_ww.zip" % (eTS.strftime("%Y%m%d%H%M"),)
os.system(cmd)

"""
sql = ['','','','']
sql[0] = "BEGIN"
sql[1] = "DELETE from warnings_summary"
sql[2] = "INSERT into warnings_summary (expire, phenomena, significance, geom)\
     SELECT expire, phenomena, significance, 'SRID=4326;'||astext(multi(buffer(collect(geom),0))) as geom\
     from warnings WHERE expire > now() and gtype = 'C' \
     GROUP by expire, phenomena, significance"
sql[3] = "COMMIT"

for s in sql:
  mydb.query(s)
"""

sys.exit(0)
