#!/mesonet/python/bin/python
# Dump LSRs to a shapefile

import shapelib, dbflib, mx.DateTime, zipfile, os, sys, shutil, cgi
from pyIEM import wellknowntext, iemdb

i = iemdb.iemdb()
mydb = i["postgis"]
#import pg
#mydb = pg.connect('postgis', 'mesonet-db1.agron.iastate.edu',user='nobody')

mydb.query("SET TIME ZONE 'GMT'")

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
month2 = int(form["month2"][0])
day1 = int(form["day1"][0])
day2 = int(form["day2"][0])
hour1 = int(form["hour1"][0])
hour2 = int(form["hour2"][0])
minute1 = int(form["minute1"][0])
minute2 = int(form["minute2"][0])

wfoLimiter = ""
if form.has_key('wfo[]'):
  aWFO = form['wfo[]']
  aWFO.append('XXX') # Hack to make next section work
  wfoLimiter = " and wfo in %s " % ( str( tuple(aWFO) ), )

sTS = mx.DateTime.DateTime(year1, month1, day1, hour1, minute1)
eTS = mx.DateTime.DateTime(year2, month2, day2, hour2, minute2)

os.chdir("/tmp/")
fp = "lsr_%s_%s" % (sTS.strftime("%Y%m%d%H%M"), eTS.strftime("%Y%m%d%H%M") )

shp = shapelib.create(fp, shapelib.SHPT_POINT)

dbf = dbflib.create(fp)
dbf.add_field("VALID", dbflib.FTString, 12, 0)
dbf.add_field("MAG", dbflib.FTDouble, 10, 2)
dbf.add_field("WFO", dbflib.FTString, 3, 0)
dbf.add_field("TYPECODE", dbflib.FTString, 1, 0)
dbf.add_field("TYPETEXT", dbflib.FTString, 40, 0)
dbf.add_field("CITY", dbflib.FTString, 40, 0)
dbf.add_field("COUNTY", dbflib.FTString, 40, 0)
dbf.add_field("SOURCE", dbflib.FTString, 40, 0)
dbf.add_field("REMARK", dbflib.FTString, 400, 0)


sql = "SELECT distinct *, astext(geom) as tgeom from lsrs WHERE \
	valid >= '%s' and valid < '%s' %s \
	ORDER by valid ASC" % (sTS.strftime("%Y-%m-%d %H:%M"), 
    eTS.strftime("%Y-%m-%d %H:%M"), wfoLimiter )
rs = mydb.query(sql).dictresult()

cnt = 0
#print 'Content-type: text/plain\n\n'
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
	d["REMARK"] = rs[i]['remark'][:400]
	#print d
    
	obj = shapelib.SHPObject(shapelib.SHPT_POINT, 1, [[f]] )
	shp.write_object(-1, obj)
	dbf.write_record(cnt, d)
	del(obj)
	cnt += 1


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
