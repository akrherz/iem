#!/usr/bin/python
"""
 Dump LSRs to a shapefile
"""
import datetime 
import zipfile
import os
import sys
import shutil
import cgi
import cgitb
cgitb.enable()
from osgeo import ogr

source = ogr.Open("PG:host=iemdb dbname=postgis user=nobody")

# Get CGI vars
form = cgi.FormContent()

if form.has_key('year'):
    year1 = int(form["year"][0])
    year2 = int(form["year"][0])
else:
    year1 = int(form["year1"][0])
    year2 = int(form["year2"][0])
month1 = int(form["month1"][0])
if (not form.has_key("month2")):
    sys.exit()
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
    if "ALL" not in aWFO:
        wfoLimiter = " and wfo in %s " % ( str( tuple(aWFO) ), )

sTS = datetime.datetime(year1, month1, day1, hour1, minute1)
eTS = datetime.datetime(year2, month2, day2, hour2, minute2)

os.chdir("/tmp/")
fp = "lsr_%s_%s" % (sTS.strftime("%Y%m%d%H%M"), eTS.strftime("%Y%m%d%H%M") )
for suffix in ['shp', 'shx', 'dbf', 'csv']:
    if os.path.isfile("%s.%s" % (fp, suffix)):
        os.remove("%s.%s" % (fp, suffix))

csv = open("%s.csv" % (fp,), 'w')
csv.write("VALID,LAT,LON,MAG,WFO,TYPECODE,TYPETEXT,CITY,COUNTY,STATE,SOURCE,REMARK\n")

out_driver = ogr.GetDriverByName( 'ESRI Shapefile' )
out_ds = out_driver.CreateDataSource("%s.shp" % (fp, ))
out_layer = out_ds.CreateLayer("point", None, ogr.wkbPoint)
fd = ogr.FieldDefn('VALID',ogr.OFTString)
fd.SetWidth(12)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('MAG',ogr.OFTReal)
fd.SetPrecision(2)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('WFO',ogr.OFTString)
fd.SetWidth(3)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('TYPECODE',ogr.OFTString)
fd.SetWidth(1)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('TYPETEXT',ogr.OFTString)
fd.SetWidth(40)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('CITY',ogr.OFTString)
fd.SetWidth(40)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('COUNTY',ogr.OFTString)
fd.SetWidth(40)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('STATE',ogr.OFTString)
fd.SetWidth(2)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('SOURCE',ogr.OFTString)
fd.SetWidth(40)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('REMARK',ogr.OFTString)
fd.SetWidth(100)
out_layer.CreateField(fd)

sql = """SELECT distinct geom, valid, magnitude, type, wfo, city, typetext,
    county, source, substr(remark,0,100) as tremark, state,
    to_char(valid at time zone 'UTC', 'YYYYMMDDHH24MI') as utctime 
    , ST_x(geom), ST_y(geom) from lsrs WHERE 
	valid >= '%s+00' and valid < '%s+00' %s 
	ORDER by valid ASC""" % (sTS.strftime("%Y-%m-%d %H:%M"), 
    eTS.strftime("%Y-%m-%d %H:%M"), wfoLimiter )

data = source.ExecuteSQL(sql)

while True:
    feat = data.GetNextFeature()
    if not feat:
        break

    featDef = ogr.Feature(out_layer.GetLayerDefn())
    featDef.SetGeometry(feat.GetGeometryRef())
    u = feat.GetField("utctime")
    featDef.SetField('VALID', u)
    m = feat.GetField("magnitude")
    featDef.SetField('MAG', m)
    t = feat.GetField("type")
    featDef.SetField('TYPECODE', t)
    w = feat.GetField("wfo")
    featDef.SetField('WFO', w)
    c = feat.GetField("city")
    featDef.SetField('CITY', c)
    tt = feat.GetField("typetext")
    featDef.SetField('TYPETEXT', tt)
    co = feat.GetField("county")
    featDef.SetField('COUNTY', co)
    src = feat.GetField("source")
    featDef.SetField('SOURCE', src)
    tr = feat.GetField("tremark")
    featDef.SetField('REMARK', tr)
    st = feat.GetField("state")
    featDef.SetField('STATE', st)

    out_layer.CreateFeature(featDef)
    feat.Destroy()
    csv.write("%s,%.2f,%.2f,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (
            u, feat.GetField("st_y"), 
            feat.GetField("st_x"), m,
            w, t, 
            tt, c,
            co, st, src,
            tr.replace(",", "_")))

source.Destroy()
out_ds.Destroy()
csv.close()

# Create zip file, send it back to the clients
shutil.copyfile("/mesonet/www/apps/iemwebsite/data/gis/meta/4326.prj", fp+".prj")
z = zipfile.ZipFile(fp+".zip", 'w', zipfile.ZIP_DEFLATED)
z.write(fp+".shp")
z.write(fp+".shx")
z.write(fp+".dbf")
z.write(fp+".prj")
z.write(fp+".csv")
z.close()

if "justcsv" in form:
    sys.stdout.write("Content-type: application/octet-stream\n")
    sys.stdout.write("Content-Disposition: attachment; filename=%s.csv\n\n" % (
                                                                        fp,))
    sys.stdout.write( file(fp+".csv", 'r').read() )    
    
else:
    sys.stdout.write("Content-type: application/octet-stream\n")
    print "Content-Disposition: attachment; filename=%s.zip" % (fp,)
    print
    
    print file(fp+".zip", 'r').read(),

os.remove(fp+".zip")
os.remove(fp+".shp")
os.remove(fp+".shx")
os.remove(fp+".dbf")
os.remove(fp+".prj")
