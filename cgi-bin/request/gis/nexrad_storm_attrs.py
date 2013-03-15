#!/usr/bin/python
"""
    Dump storm attributes from the database to a shapefile for the users
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
import pytz

source = ogr.Open("PG:host=iemdb dbname=postgis user=nobody tables=nexrad_attributes_log(geom)")

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

sTS = datetime.datetime(year1, month1, day1, hour1, minute1)
sTS = sTS.replace(tzinfo=pytz.timezone("UTC"))
eTS = datetime.datetime(year2, month2, day2, hour2, minute2)
eTS = eTS.replace(tzinfo=pytz.timezone("UTC"))

"""
Need to limit what we are allowing them to request as the file would get
massive.  So lets set arbitrary values of
1) If 2 or more RADARs, less than 7 days
"""
radarLimiter = ""
aRADAR = [1,2,3,4]
if form.has_key('radar[]'):
    aRADAR = form['radar[]']
    aRADAR.append('XXX') # Hack to make next section work
    if 'ALL' not in aRADAR:
        radarLimiter = " and nexrad in %s " % ( str( tuple(aRADAR) ), )
if len(aRADAR) > 2 and (eTS - sTS).days > 6:
    eTS = sTS + datetime.timedelta(days=7)

os.chdir("/tmp/")
fp = "stormattr_%s_%s" % (sTS.strftime("%Y%m%d%H%M"),
                           eTS.strftime("%Y%m%d%H%M") )
for suffix in ['shp', 'shx', 'dbf']:
    if os.path.isfile("%s.%s" % (fp, suffix)):
        os.remove("%s.%s" % (fp, suffix))

out_driver = ogr.GetDriverByName( 'ESRI Shapefile' )
out_ds = out_driver.CreateDataSource("%s.shp" % (fp, ))
out_layer = out_ds.CreateLayer("point", None, ogr.wkbPoint)
fd = ogr.FieldDefn('VALID',ogr.OFTString)
fd.SetWidth(12)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('STORM_ID',ogr.OFTString)
fd.SetWidth(2)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('NEXRAD',ogr.OFTString)
fd.SetWidth(3)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('AZIMUTH',ogr.OFTInteger)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('RANGE',ogr.OFTInteger)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('TVS',ogr.OFTString)
fd.SetWidth(10)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('MESO',ogr.OFTString)
fd.SetWidth(10)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('POSH',ogr.OFTInteger)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('POH',ogr.OFTInteger)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('MAX_SIZE',ogr.OFTReal)
fd.SetWidth(5)
fd.SetPrecision(2)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('VIL',ogr.OFTInteger)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('MAX_DBZ',ogr.OFTInteger)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('MAX_DBZ_H',ogr.OFTReal)
fd.SetWidth(5)
fd.SetPrecision(2)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('TOP',ogr.OFTReal)
fd.SetWidth(5)
fd.SetPrecision(2)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('DRCT',ogr.OFTInteger)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('SKNT',ogr.OFTInteger)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('LAT',ogr.OFTReal)
fd.SetWidth(7)
fd.SetPrecision(4)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('LON',ogr.OFTReal)
fd.SetWidth(9)
fd.SetPrecision(4)
out_layer.CreateField(fd)


sql = """SELECT to_char(valid at time zone 'UTC', 'YYYYMMDDHH24MI') as utctime,
    * , x(geom) as lon, y(geom) as lat
    from nexrad_attributes_log WHERE 
    valid >= '%s' and valid < '%s' %s  ORDER by valid ASC""" % (
                    sTS.strftime("%Y-%m-%d %H:%M+00"), 
                    eTS.strftime("%Y-%m-%d %H:%M+00"), radarLimiter) 

#print 'Content-type: text/plain\n'
#print sql
#sys.exit()
data = source.ExecuteSQL(sql)

while True:
    feat = data.GetNextFeature()
    if not feat:
        break

    featDef = ogr.Feature(out_layer.GetLayerDefn())
    featDef.SetGeometry(feat.GetGeometryRef())
    featDef.SetField('VALID', feat.GetField("utctime"))
    featDef.SetField('NEXRAD', feat.GetField("nexrad"))
    featDef.SetField('STORM_ID', feat.GetField("storm_id"))
    featDef.SetField('AZIMUTH', feat.GetField("azimuth"))
    featDef.SetField('RANGE', feat.GetField("range"))
    featDef.SetField('TVS', feat.GetField("tvs"))
    featDef.SetField('MESO', feat.GetField("meso"))
    featDef.SetField('POSH', feat.GetField("posh"))
    featDef.SetField('POH', feat.GetField("poh"))
    featDef.SetField('MAX_SIZE', feat.GetField("max_size"))
    featDef.SetField('VIL', feat.GetField("vil"))
    featDef.SetField('MAX_DBZ', feat.GetField("max_dbz"))
    featDef.SetField('MAX_DBZ_H', feat.GetField("max_dbz_height"))
    featDef.SetField('TOP', feat.GetField("top"))
    featDef.SetField('DRCT', feat.GetField("drct"))
    featDef.SetField('SKNT', feat.GetField("sknt"))
    featDef.SetField('LAT', feat.GetField("lat"))
    featDef.SetField('LON', feat.GetField("lon"))

    out_layer.CreateFeature(featDef)
    feat.Destroy()

source.Destroy()
out_ds.Destroy()

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
