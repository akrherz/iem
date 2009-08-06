# Something to dump current warnings to a shapefile
# 28 Aug 2004 port to iem40

import shapelib, dbflib, mx.DateTime, zipfile, os, sys, shutil
from pyIEM import wellknowntext, iemdb
i = iemdb.iemdb()
mydb = i["postgis"]
if (mydb == None): 
	sys.exit(0)
mydb.query("SET TIME ZONE 'GMT'")

"""
 nexrad         | character(3)             |
 storm_id       | character(2)             |
 geom           | geometry                 |
 azimuth        | smallint                 |
 range          | smallint                 |
 tvs            | character varying(10)    |
 meso           | character varying(10)    |
 posh           | smallint                 |
 poh            | smallint                 |
 max_size       | real                     |
 vil            | smallint                 |
 max_dbz        | smallint                 |
 max_dbz_height | real                     |
 top            | real                     |
 drct           | smallint                 |
 sknt           | smallint                 |
 valid          | timestamp with time zone |
"""

os.chdir("/tmp")

# Delete anything older than 20 minutes
now = mx.DateTime.gmt()
eTS = mx.DateTime.gmt() - mx.DateTime.RelativeDateTime(minutes=+20)

shp = shapelib.create("current_nexattr", shapelib.SHPT_POINT)

dbf = dbflib.create("current_nexattr")
dbf.add_field("VALID", dbflib.FTString, 12, 0)
dbf.add_field("STORM_ID", dbflib.FTString, 2, 0)
dbf.add_field("NEXRAD", dbflib.FTString, 3, 0)
dbf.add_field("AZIMUTH", dbflib.FTInteger, 3, 0)
dbf.add_field("RANGE", dbflib.FTInteger, 3, 0)
dbf.add_field("TVS", dbflib.FTString, 10, 0)
dbf.add_field("MESO", dbflib.FTString, 10, 0)
dbf.add_field("POSH", dbflib.FTInteger, 3, 0)
dbf.add_field("POH", dbflib.FTInteger, 3, 0)
dbf.add_field("MAX_SIZE", dbflib.FTDouble, 5, 2)
dbf.add_field("VIL", dbflib.FTInteger, 3, 0)
dbf.add_field("MAX_DBZ", dbflib.FTInteger, 3, 0)
dbf.add_field("MAX_DBZ_H", dbflib.FTDouble, 5, 2)
dbf.add_field("TOP", dbflib.FTDouble, 5, 2)
dbf.add_field("DRCT", dbflib.FTDouble, 3, 0)
dbf.add_field("SKNT", dbflib.FTDouble, 3, 0)

sql = "DELETE from nexrad_attributes WHERE valid < '%s'" % \
	(eTS.strftime("%Y-%m-%d %H:%M"), )
mydb.query(sql)
sql = "SELECT *, astext(geom) as tgeom from nexrad_attributes "
rs = mydb.query(sql).dictresult()

cnt = 0
for i in range(len(rs)):
    #print rs[i]
    s = rs[i]["tgeom"]
    if (s == None or s == ""):
        continue
    f = wellknowntext.convert_well_known_text(s)

    d = {}
    valid = mx.DateTime.strptime(rs[i]["valid"][:16], "%Y-%m-%d %H:%M")
    d["VALID"] = valid.strftime("%Y%m%d%H%M")
    d["NEXRAD"] = rs[i]['nexrad']
    d["STORM_ID"] = rs[i]['storm_id']
    d["AZIMUTH"] = float(rs[i]['azimuth'])
    d["RANGE"] = float(rs[i]['range'])
    d["TVS"] = rs[i]['tvs']
    d["MESO"] = rs[i]['meso']
    d["POSH"] = float(rs[i]['posh'])
    d["POH"] = float(rs[i]['poh'])
    d["MAX_SIZE"] = float(rs[i]['max_size'])
    d["VIL"] = float(rs[i]['vil'])
    d["MAX_DBZ"] = float(rs[i]['max_dbz'])
    d["MAX_DBZ_H"] = float(rs[i]['max_dbz_height'])
    d["TOP"] = float(rs[i]['top'])
    d["DRCT"] = float(rs[i]['drct'])
    d["SKNT"] = float(rs[i]['sknt'])
    #print d
    obj = shapelib.SHPObject(shapelib.SHPT_POINT, 1, [[f,]] )
    shp.write_object(-1, obj)
    dbf.write_record(cnt, d)
    del(obj)
    cnt += 1

if (cnt == 0):
    obj = shapelib.SHPObject(shapelib.SHPT_POINT, 1, [[(0.1, 0.1),]] )
    d = {}
    d["VALID"] = "200000000000"
    d["NEXRAD"] = "XXX"
    d["STORM_ID"] = "XX"
    d["AZIMUTH"] = 0
    d["RANGE"] = 0
    d["TVS"] = "NONE"
    d["MESO"] = "NONE"
    d["POSH"] = 0
    d["POH"] = 0
    d["MAX_SIZE"] = 0
    d["VIL"] = 0
    d["MAX_DBZ"] = 0
    d["MAX_DBZ_H"] = 0
    d["TOP"] = 0
    d["DRCT"] = 0
    d["SKNT"] = 0

    shp.write_object(-1, obj)
    dbf.write_record(0, d)

del(shp)
del(dbf)
shutil.copy("/mesonet/data/gis/meta/4326.prj", "current_nexattr.prj")
z = zipfile.ZipFile("current_nexattr.zip", 'w', zipfile.ZIP_DEFLATED)
z.write("current_nexattr.shp")
z.write("current_nexattr.shx")
z.write("current_nexattr.dbf")
z.write("current_nexattr.prj")
z.close()

cmd = "/home/ldm/bin/pqinsert -p \"zip c %s gis/shape/4326/us/current_nexattr.zip bogus zip\" current_nexattr.zip" % (now.strftime("%Y%m%d%H%M"),)
os.system(cmd)


sys.exit(0)
