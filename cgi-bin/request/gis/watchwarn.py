#!/mesonet/python/bin/python
# Something to dump current warnings to a shapefile

import shapelib, dbflib, mx.DateTime, zipfile, os, sys, shutil, cgi
os.environ['TZ'] = 'UTC'
from pyIEM import wellknowntext
import psycopg2
import psycopg2.extras

mydb = psycopg2.connect("dbname='postgis' host='iemdb' user='nobody'")


# Get CGI vars
form = cgi.FormContent()
if form.has_key('year'):
  year1 = int(form["year"][0])
  year2 = int(form["year"][0])
else:
  year1 = int(form["year1"][0])
  year2 = int(form["year2"][0])
month1 = int(form["month1"][0])
if (not form.has_key("month2")):  sys.exit()
if (year1 < 1986 or year1 > mx.DateTime.now().year): sys.exit()
month2 = int(form["month2"][0])
day1 = int(form["day1"][0])
day2 = int(form["day2"][0])
hour1 = int(form["hour1"][0])
hour2 = int(form["hour2"][0])
minute1 = int(form["minute1"][0])
minute2 = int(form["minute2"][0])

sTS = mx.DateTime.DateTime(year1, month1, day1, hour1, minute1)
eTS = mx.DateTime.DateTime(year2, month2, day2, hour2, minute2)

wfoLimiter = ""
if form.has_key('wfo[]'):
  aWFO = form['wfo[]']
  aWFO.append('XXX') # Hack to make next section work
  wfoLimiter = " and wfo in %s " % ( str( tuple(aWFO) ), )


os.chdir("/tmp/")
fp = "wwa_%s_%s" % (sTS.strftime("%Y%m%d%H%M"), eTS.strftime("%Y%m%d%H%M") )

shp = shapelib.create(fp, shapelib.SHPT_POLYGON)

dbf = dbflib.create(fp)
dbf.add_field("WFO", dbflib.FTString, 3, 0)
dbf.add_field("ISSUED", dbflib.FTString, 12, 0)
dbf.add_field("EXPIRED", dbflib.FTString, 12, 0)
dbf.add_field("PHENOM", dbflib.FTString, 2, 0)
dbf.add_field("GTYPE", dbflib.FTString, 1, 0)
dbf.add_field("SIG", dbflib.FTString, 1, 0)
dbf.add_field("ETN", dbflib.FTInteger, 4, 0)
dbf.add_field("STATUS", dbflib.FTString, 3, 0)
dbf.add_field("NWS_UGC", dbflib.FTString, 6, 0)
dbf.add_field("AREA_KM2", dbflib.FTDouble, 10, 2)

limiter = ""
if form.has_key("limit0"):
  limiter += " and phenomena IN ('TO','SV','FF','MA') and significance = 'W' "
if form.has_key("limit1"):
  limiter += " and gtype = 'P' "

sql = """SELECT *, astext(geom) as tgeom,
    area( transform(geom,2163) ) / 1000000.0 as area2d
    from warnings WHERE isValid(geom) and 
	issue >= '%s' and issue < '%s' and eventid < 10000 
	%s %s""" % ( sTS.strftime("%Y-%m-%d %H:%M"), eTS.strftime("%Y-%m-%d %H:%M"), limiter , wfoLimiter)
cursor = mydb.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.DictCursor)
cursor.execute(sql)

cnt = 0
for row in cursor:
	s = row["tgeom"]
	if (s == None or s == ""):
		continue
	f = wellknowntext.convert_well_known_text(s)

	g = row["gtype"]
	t = row["phenomena"]
	#issue = mx.DateTime.strptime(row["issue"][:16], "%Y-%m-%d %H:%M")
	#expire = mx.DateTime.strptime(row["expire"][:16],"%Y-%m-%d %H:%M")
	issue = row["issue"]
	expire = row["expire"]
	u = issue.utcoffset() or ZERO
	issue -= u
	expire -= u
	d = {}
	d["ISSUED"] = issue.strftime("%Y%m%d%H%M")
	d["EXPIRED"] = expire.strftime("%Y%m%d%H%M")
	d["PHENOM"] = t
	d["GTYPE"] = g
	d["SIG"] = row["significance"]
	d["WFO"] = row["wfo"]
	d["ETN"] = row["eventid"]
	d["STATUS"] = row["status"]
	d["NWS_UGC"] = row["ugc"]
	d["AREA_KM2"] = row["area2d"]
	if ((d["SIG"] is None or d["SIG"] == "") and d["PHENOM"] == 'FF'):
		d["SIG"] = "W"
		d["ETN"] = -1
		d["STATUS"] = "ZZZ"

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
	d["PHENOM"] = "ZZ"
	d["GTYPE"] = "Z"
	d["WFO"] = "ZZZ"
	d["SIG"] = "Z"
	d["ETN"] = 0
	d["AREA_KM2"] = 0
	d["STATUS"] = "ZZZ"
	d["NWS_UGC"] = "ZZZZZZ"
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
