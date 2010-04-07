#!/mesonet/python/bin/python
# Generate a shapefile of the WOU outline.
# 28 Aug 2004 port to iem40

import shapelib, dbflib, mx.DateTime, zipfile, os, sys, shutil, cgi
from pyIEM import wellknowntext, iemdb

i = iemdb.iemdb()
mydb = i["postgis"]

mydb.query("SET TIME ZONE 'GMT'")

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

sql = """select astext(multi(geomunion(geom))) as tgeom 
       from warnings_%s WHERE significance = 'A' and 
       phenomena IN ('TO','SV') and eventid = %s and
       isvalid(geom) and 
       issue < ((select issued from watches WHERE num = %s
                and extract(year from issued) = %s LIMIT 1) + '60 minutes'::interval)
       """ % (year, etn, etn, year) 
rs = mydb.query(sql).dictresult()

if len(rs) == 0:
    sys.exit()

s = rs[0]["tgeom"]
f = wellknowntext.convert_well_known_text(s)

d = {}
d["SIG"] = 'A'
d["ETN"] = etn

obj = shapelib.SHPObject(shapelib.SHPT_POLYGON, 1, f )
shp.write_object(-1, obj)
dbf.write_record(0, d)
del(obj)

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
