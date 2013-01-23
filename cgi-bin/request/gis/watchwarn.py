#!/usr/bin/env python
"""
Generate a shapefile of warnings based on the CGI request
"""

import zipfile
import os
import shutil
import cgi
#import cgitb
#cgitb.enable()
import sys
import datetime
from osgeo import ogr

now = datetime.datetime.now()
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
if not form.has_key("month2"):
    sys.exit()
if year1 < 1986 or year1 > now.year: 
    sys.exit()
month2 = int(form["month2"][0])
day1 = int(form["day1"][0])
day2 = int(form["day2"][0])
hour1 = int(form["hour1"][0])
hour2 = int(form["hour2"][0])
minute1 = int(form["minute1"][0])
minute2 = int(form["minute2"][0])

sTS = datetime.datetime(year1, month1, day1, hour1, minute1)
eTS = datetime.datetime(year2, month2, day2, hour2, minute2)

wfoLimiter = ""
if form.has_key('wfo[]'):
    aWFO = form['wfo[]']
    aWFO.append('XXX') # Hack to make next section work
    if 'ALL' not in aWFO:
        wfoLimiter = " and wfo in %s " % ( str( tuple(aWFO) ), )

if form.has_key('wfos[]'):
    aWFO = form['wfos[]']
    aWFO.append('XXX') # Hack to make next section work
    if 'ALL' not in aWFO:
        wfoLimiter = " and wfo in %s " % ( str( tuple(aWFO) ), )

os.chdir("/tmp/")
fp = "wwa_%s_%s" % (sTS.strftime("%Y%m%d%H%M"), eTS.strftime("%Y%m%d%H%M") )
for suffix in ['shp', 'shx', 'dbf']:
    if os.path.isfile("%s.%s" % (fp, suffix)):
        os.remove("%s.%s" % (fp, suffix))

out_driver = ogr.GetDriverByName( 'ESRI Shapefile' )
out_ds = out_driver.CreateDataSource("%s.shp" % (fp, ))
out_layer = out_ds.CreateLayer("polygon", None, ogr.wkbPolygon)
fd = ogr.FieldDefn('WFO',ogr.OFTString)
fd.SetWidth(3)
out_layer.CreateField(fd)
fd = ogr.FieldDefn('ISSUED',ogr.OFTString)
fd.SetWidth(12)
out_layer.CreateField(fd)
fd = ogr.FieldDefn('EXPIRED',ogr.OFTString)
fd.SetWidth(12)
out_layer.CreateField(fd)
fd = ogr.FieldDefn('PHENOM',ogr.OFTString)
fd.SetWidth(2)
out_layer.CreateField(fd)
fd = ogr.FieldDefn('GTYPE',ogr.OFTString)
fd.SetWidth(1)
out_layer.CreateField(fd)
fd = ogr.FieldDefn('SIG',ogr.OFTString)
fd.SetWidth(1)
out_layer.CreateField(fd)
fd = ogr.FieldDefn('ETN',ogr.OFTString)
fd.SetWidth(4)
out_layer.CreateField(fd)
fd = ogr.FieldDefn('STATUS',ogr.OFTString)
fd.SetWidth(3)
out_layer.CreateField(fd)
fd = ogr.FieldDefn('NWS_UGC',ogr.OFTString)
fd.SetWidth(6)
out_layer.CreateField(fd)
fd = ogr.FieldDefn('AREA_KM2',ogr.OFTReal)
fd.SetPrecision(2)
out_layer.CreateField(fd)

limiter = ""
if form.has_key("limit0"):
    limiter += " and phenomena IN ('TO','SV','FF','MA') and significance = 'W' "
if form.has_key("limit1"):
    limiter += " and gtype = 'P' "

table = "warnings"
if sTS.year == eTS.year:
    table = "warnings_%s" % (sTS.year,)

sql = """SELECT *, astext(ST_Simplify(geom,0.0001)) as tgeom,
    area( transform(geom,2163) ) / 1000000.0 as area2d,
    to_char(issue at time zone 'UTC', 'YYYYMMDDHH24MI') as utc_issue,
    to_char(expire at time zone 'UTC', 'YYYYMMDDHH24MI') as utc_expire
    from %s WHERE isValid(geom) and 
	issue >= '%s+00' and issue < '%s+00' and eventid < 10000 
	%s %s""" % ( table, sTS.strftime("%Y-%m-%d %H:%M"), 
                 eTS.strftime("%Y-%m-%d %H:%M"), limiter , wfoLimiter)

data = source.ExecuteSQL(sql)

while True:
    feat = data.GetNextFeature()
    if not feat:
        break

    featDef = ogr.Feature(out_layer.GetLayerDefn())
    featDef.SetGeometry(feat.GetGeometryRef())
    featDef.SetField('ISSUED', feat.GetField("utc_issue"))
    featDef.SetField('EXPIRED', feat.GetField("utc_expire"))
    featDef.SetField('PHENOM', feat.GetField("phenomena"))
    featDef.SetField('GTYPE', feat.GetField("gtype"))
    featDef.SetField('SIG', feat.GetField("significance"))
    featDef.SetField('WFO', feat.GetField("wfo"))
    featDef.SetField('ETN', feat.GetField("eventid"))
    featDef.SetField('STATUS', feat.GetField("status"))
    featDef.SetField('NWS_UGC', feat.GetField("ugc"))
    featDef.SetField('AREA_KM2', feat.GetField("area2d"))
    if ((feat.GetField("significance") is None or 
        feat.GetField("significance") == "") and feat.GetField("phenomena") == 'FF'):
        featDef.SetField('SIG', 'W')
        featDef.SetField('ETN', "-1")
        featDef.SetField('STATUS', "ZZZ")

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


# END