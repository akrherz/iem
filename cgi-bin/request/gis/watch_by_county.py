#!/usr/bin/env python

import zipfile
import os
import sys
import shutil
import datetime
import cgi
from osgeo import ogr

# Get CGI vars
form = cgi.FormContent()
if "year" in form:
    year = int(form["year"][0])
    month = int(form["month"][0])
    day = int(form["day"][0])
    hour = int(form["hour"][0])
    minute = int(form["minute"][0])
    ts = datetime.datetime(year, month, day, hour, minute)
    fp = "watch_by_county_%s" % (ts.strftime("%Y%m%d%H%M"),)
else:
    ts = datetime.datetime.utcnow()
    fp = "watch_by_county"

if "etn" in form:
    etnLimiter = "and eventid = %s" % (int(form["etn"][0]), )
    fp = "watch_by_county_%s_%s" % (ts.strftime("%Y%m%d%H%M"),
                                    int(form["etn"][0]))
else:
    etnLimiter = ""

os.chdir("/tmp/")
for suffix in ['shp', 'shx', 'dbf']:
    if os.path.isfile("%s.%s" % (fp, suffix)):
        os.remove("%s.%s" % (fp, suffix))

table = "warnings_%s" % (ts.year, )
source = ogr.Open(
    "PG:host=iemdb dbname=postgis user=nobody tables=%s(tgeom)" % (table,))

out_driver = ogr.GetDriverByName('ESRI Shapefile')
out_ds = out_driver.CreateDataSource("%s.shp" % (fp, ))
out_layer = out_ds.CreateLayer("polygon", None, ogr.wkbPolygon)

fd = ogr.FieldDefn('ISSUED', ogr.OFTString)
fd.SetWidth(12)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('EXPIRED', ogr.OFTString)
fd.SetWidth(12)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('PHENOM', ogr.OFTString)
fd.SetWidth(2)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('SIG', ogr.OFTString)
fd.SetWidth(1)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('ETN', ogr.OFTInteger)
out_layer.CreateField(fd)

sql = """
    select phenomena, eventid, ST_multi(ST_union(u.geom)) as tgeom,
    max(to_char(expire at time zone 'UTC', 'YYYYMMDDHH24MI')) as utcexpire,
    min(to_char(issue at time zone 'UTC', 'YYYYMMDDHH24MI')) as utcissue
    from warnings_%s w JOIN ugcs u on (u.gid = w.gid) WHERE significance = 'A'
    and phenomena IN ('TO','SV')
    and issue > '%s'::timestamp -'3 days':: interval
    and issue <= '%s' and
    expire > '%s' %s GROUP by phenomena, eventid ORDER by phenomena ASC
""" % (ts.year, ts.strftime("%Y-%m-%d %H:%M+00"),
       ts.strftime("%Y-%m-%d %H:%M+00"),
       ts.strftime("%Y-%m-%d %H:%M+00"), etnLimiter)

# print 'Content-type: text/plain\n'
# print sql
# sys.exit()
data = source.ExecuteSQL(sql)

while True:
    feat = data.GetNextFeature()
    if not feat:
        break
    geom = feat.GetGeometryRef()

    featDef = ogr.Feature(out_layer.GetLayerDefn())
    featDef.SetGeometry(geom)
    featDef.SetField('PHENOM', feat.GetField("phenomena"))
    featDef.SetField('SIG', 'A')
    featDef.SetField('ETN', feat.GetField("eventid"))
    featDef.SetField('ISSUED', feat.GetField("utcissue"))
    featDef.SetField('EXPIRED', feat.GetField("utcexpire"))

    out_layer.CreateFeature(featDef)
    feat.Destroy()

source.Destroy()
out_ds.Destroy()

# Create zip file, send it back to the clients
shutil.copyfile("/mesonet/www/apps/iemwebsite/data/gis/meta/4326.prj",
                fp+".prj")
z = zipfile.ZipFile(fp+".zip", 'w', zipfile.ZIP_DEFLATED)
z.write(fp+".shp")
z.write(fp+".shx")
z.write(fp+".dbf")
z.write(fp+".prj")
z.close()

sys.stdout.write("Content-type: application/octet-stream\n")
sys.stdout.write(
    "Content-Disposition: attachment; filename=%s.zip\n\n" % (fp,))
sys.stdout.write(file(fp+".zip", 'r').read())

os.remove(fp+".zip")
os.remove(fp+".shp")
os.remove(fp+".shx")
os.remove(fp+".dbf")
os.remove(fp+".prj")
