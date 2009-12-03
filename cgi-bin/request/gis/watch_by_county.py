#!/mesonet/python/bin/python
# Something to dump current warnings to a shapefile
# 28 Aug 2004 port to iem40

import shapelib, dbflib, mx.DateTime, zipfile, os, sys, shutil, cgi
from pyIEM import wellknowntext, iemdb

i = iemdb.iemdb()
mydb = i["postgis"]

mydb.query("SET TIME ZONE 'GMT'")

# Get CGI vars
form = cgi.FormContent()
if form.has_key("year"):
  year = int(form["year"][0])
  month = int(form["month"][0])
  day = int(form["day"][0])
  hour = int(form["hour"][0])
  minute = int(form["minute"][0])
  ts = mx.DateTime.DateTime(year, month, day, hour, minute)
  fp = "watch_by_county_%s" % (ts.strftime("%Y%m%d%H%M"),)
else:
  ts = mx.DateTime.gmt()
  fp = "watch_by_county"


os.chdir("/tmp/")

shp = shapelib.create(fp, shapelib.SHPT_POLYGON)

dbf = dbflib.create(fp)
dbf.add_field("ISSUED", dbflib.FTString, 12, 0)
dbf.add_field("EXPIRED", dbflib.FTString, 12, 0)
dbf.add_field("PHENOM", dbflib.FTString, 2, 0)
dbf.add_field("SIG", dbflib.FTString, 1, 0)
dbf.add_field("ETN", dbflib.FTInteger, 4, 0)

sql = """select phenomena, eventid, astext(multi(geomunion(geom))) as tgeom, 
       min(issue) as issued, max(expire) as expired 
       from warnings WHERE significance = 'A' and 
       phenomena IN ('TO','SV') and issue > '%s'::timestamp -'3 days':: interval 
       and issue <= '%s' and 
       expire > '%s' GROUP by phenomena, eventid ORDER by phenomena ASC
       """ % (ts.strftime("%Y-%m-%d %H:%I"), ts.strftime("%Y-%m-%d %H:%I"),
              ts.strftime("%Y-%m-%d %H:%I") )
rs = mydb.query(sql).dictresult()

cnt = 0
for i in range(len(rs)):
	s = rs[i]["tgeom"]
	if (s == None or s == ""):
		continue
	f = wellknowntext.convert_well_known_text(s)

	t = rs[i]["phenomena"]
	issue = mx.DateTime.strptime(rs[i]["issued"][:16], "%Y-%m-%d %H:%M")
	expire = mx.DateTime.strptime(rs[i]["expired"][:16],"%Y-%m-%d %H:%M")
	d = {}
	d["ISSUED"] = issue.strftime("%Y%m%d%H%M")
	d["EXPIRED"] = expire.strftime("%Y%m%d%H%M")
	d["PHENOM"] = t
	d["SIG"] = 'A'
	d["ETN"] = rs[i]["eventid"]

	obj = shapelib.SHPObject(shapelib.SHPT_POLYGON, 1, f )
	shp.write_object(-1, obj)
	dbf.write_record(cnt, d)
	del(obj)
	cnt += 1

if (cnt == 0):
	obj = shapelib.SHPObject(shapelib.SHPT_POLYGON, 1, [[(0.1, 0.1), (0.2, 0.2), (0.3, 0.1), (0.1, 0.1)]])
	d = {}
	d["PHENOM"] = "ZZ"
	d["ISSUED"] = "200000000000"
	d["EXPIRED"] = "200000000000"

	d["ETN"] = 0
	shp.write_object(-1, obj)
	dbf.write_record(0, d)

del(shp)
del(dbf)

# Create zip file, send it back to the clients
shutil.copyfile("/mesonet/data/gis/meta/4326.prj", fp+".prj")
z = zipfile.ZipFile(fp+".zip", 'w', zipfile.ZIP_DEFLATED)
z.write(fp+".shp")
z.write(fp+".shx")
z.write(fp+".dbf")
z.write(fp+".prj")
z.close()

print "Content-type: application/octet-stream"
print "Content-Disposition: attachment; filename=%s.zip" % (fp,)
print

print file(fp+".zip", 'r').read(),

os.remove(fp+".zip")
os.remove(fp+".shp")
os.remove(fp+".shx")
os.remove(fp+".dbf")
os.remove(fp+".prj")
