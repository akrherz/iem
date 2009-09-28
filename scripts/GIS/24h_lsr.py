# Something to dump current warnings to a shapefile
# 28 Aug 2004 port to iem40

import shapelib, dbflib, mx.DateTime, zipfile, os, sys, shutil
from pyIEM import wellknowntext, iemdb
i = iemdb.iemdb()
mydb = i["postgis"]
if (mydb == None): 
	sys.exit(0)
mydb.query("SET TIME ZONE 'GMT'")

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
sql = "SELECT distinct *, astext(geom) as tgeom from lsrs_%s WHERE valid > (now() -'1 day'::interval) " % (eTS.year,)
rs = mydb.query(sql).dictresult()

cnt = 0
for i in range(len(rs)):
	
	s = rs[i]["tgeom"]
	if (s == None or s == ""):
		continue
	f = wellknowntext.convert_well_known_text(s)

	issue = mx.DateTime.strptime(rs[i]["valid"][:16], "%Y-%m-%d %H:%M")
	d = {}
	d["VALID"] = issue.strftime("%Y%m%d%H%M")
	d["MAG"] = float(rs[i]['magnitude'])
	d["TYPECODE"] = rs[i]['type']
	d["WFO"] = rs[i]['wfo']
	d["TYPETEXT"] = rs[i]['typetext']
	d["CITY"] = rs[i]['city']
	d["COUNTY"] = rs[i]['county']
	d["SOURCE"] = rs[i]['source']
	d["REMARK"] = rs[i]['remark'][:200]
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
os.system(cmd)

