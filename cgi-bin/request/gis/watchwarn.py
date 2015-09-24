#!/usr/bin/env python
"""
Generate a shapefile of warnings based on the CGI request
"""

import zipfile
import os
import shutil
import cgi
import pytz
import sys
import datetime
from osgeo import ogr

now = datetime.datetime.now()
source = ogr.Open("PG:host=iemdb dbname=postgis user=nobody")

# Get CGI vars
form = cgi.FormContent()
if 'year' in form:
    year1 = int(form["year"][0])
    year2 = int(form["year"][0])
else:
    year1 = int(form["year1"][0])
    year2 = int(form["year2"][0])

month1 = int(form["month1"][0])
if 'month2' not in form:
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
sTS = sTS.replace(tzinfo=pytz.timezone("UTC"))
eTS = datetime.datetime(year2, month2, day2, hour2, minute2)
eTS = eTS.replace(tzinfo=pytz.timezone("UTC"))

wfoLimiter = ""
if 'wfo[]' in form:
    aWFO = form['wfo[]']
    aWFO.append('XXX')  # Hack to make next section work
    if 'ALL' not in aWFO:
        wfoLimiter = " and w.wfo in %s " % (str(tuple(aWFO)), )

if 'wfos[]' in form:
    aWFO = form['wfos[]']
    aWFO.append('XXX')  # Hack to make next section work
    if 'ALL' not in aWFO:
        wfoLimiter = " and w.wfo in %s " % (str(tuple(aWFO)), )

fp = "wwa_%s_%s" % (sTS.strftime("%Y%m%d%H%M"), eTS.strftime("%Y%m%d%H%M"))
timeopt = int(form.get('timeopt', [1])[0])
if timeopt == 2:
    year3 = int(form['year3'][0])
    month3 = int(form['month3'][0])
    day3 = int(form['day3'][0])
    hour3 = int(form['hour3'][0])
    minute3 = int(form['minute3'][0])
    sTS = datetime.datetime(year3, month3, day3, hour3, minute3)
    sTS = sTS.replace(tzinfo=pytz.timezone("UTC"))
    fp = "wwa_%s" % (sTS.strftime("%Y%m%d%H%M"), )

os.chdir("/tmp/")
for suffix in ['shp', 'shx', 'dbf']:
    if os.path.isfile("%s.%s" % (fp, suffix)):
        os.remove("%s.%s" % (fp, suffix))

out_driver = ogr.GetDriverByName('ESRI Shapefile')
out_ds = out_driver.CreateDataSource("%s.shp" % (fp, ))
out_layer = out_ds.CreateLayer("polygon", None, ogr.wkbPolygon)
fd = ogr.FieldDefn('WFO', ogr.OFTString)
fd.SetWidth(3)
out_layer.CreateField(fd)
fd = ogr.FieldDefn('ISSUED', ogr.OFTString)
fd.SetWidth(12)

out_layer.CreateField(fd)
fd = ogr.FieldDefn('EXPIRED', ogr.OFTString)
fd.SetWidth(12)

out_layer.CreateField(fd)
fd = ogr.FieldDefn('INIT_ISS', ogr.OFTString)
fd.SetWidth(12)

out_layer.CreateField(fd)
fd = ogr.FieldDefn('INIT_EXP', ogr.OFTString)
fd.SetWidth(12)

out_layer.CreateField(fd)
fd = ogr.FieldDefn('PHENOM', ogr.OFTString)
fd.SetWidth(2)
out_layer.CreateField(fd)
fd = ogr.FieldDefn('GTYPE', ogr.OFTString)
fd.SetWidth(1)
out_layer.CreateField(fd)
fd = ogr.FieldDefn('SIG', ogr.OFTString)
fd.SetWidth(1)
out_layer.CreateField(fd)
fd = ogr.FieldDefn('ETN', ogr.OFTString)
fd.SetWidth(4)
out_layer.CreateField(fd)
fd = ogr.FieldDefn('STATUS', ogr.OFTString)
fd.SetWidth(3)
out_layer.CreateField(fd)
fd = ogr.FieldDefn('NWS_UGC', ogr.OFTString)
fd.SetWidth(6)
out_layer.CreateField(fd)
fd = ogr.FieldDefn('AREA_KM2', ogr.OFTReal)
fd.SetPrecision(2)
out_layer.CreateField(fd)

limiter = ""
if 'limit0' in form:
    limiter += (
        " and phenomena IN ('TO','SV','FF','MA') and significance = 'W' ")

sbwlimiter = " WHERE gtype = 'P' " if 'limit1' in form else ""

table1 = "warnings"
table2 = "sbw"
if sTS.year == eTS.year:
    table1 = "warnings_%s" % (sTS.year,)
    if sTS.year > 2001:
        table2 = "sbw_%s" % (sTS.year,)
    else:
        table2 = 'sbw_2014'

geomcol = "geom"
if 'simple' in form and form['simple'][0] == 'yes':
    geomcol = "simple_geom"

cols = """%s, gtype, significance, wfo, status, eventid, ugc, phenomena,
 area2d, utc_expire, utc_issue, utc_prodissue, utc_init_expire""" % (geomcol,)

timelimit = "issue >= '%s' and issue < '%s'" % (sTS, eTS)
if timeopt == 2:
    timelimit = "issue <= '%s' and issue > '%s' and expire > '%s'" % (
        sTS, sTS + datetime.timedelta(days=-30), sTS)

sql = """
WITH stormbased as (
 SELECT geom, 'P'::text as gtype, significance, wfo, status, eventid,
 ''::text as ugc,
 phenomena, geom as simple_geom,
 ST_area( ST_transform(w.geom,2163) ) / 1000000.0 as area2d,
 to_char(expire at time zone 'UTC', 'YYYYMMDDHH24MI') as utc_expire,
 to_char(issue at time zone 'UTC', 'YYYYMMDDHH24MI') as utc_issue,
 to_char(issue at time zone 'UTC', 'YYYYMMDDHH24MI') as utc_prodissue,
 to_char(init_expire at time zone 'UTC', 'YYYYMMDDHH24MI') as utc_init_expire
 from %s w WHERE status = 'NEW' and %s %s %s
),
countybased as (
 SELECT u.simple_geom as simple_geom, u.geom as geom, 'C'::text as gtype,
 significance,
 w.wfo, status, eventid, u.ugc, phenomena,
 ST_area( ST_transform(u.geom,2163) ) / 1000000.0 as area2d,
 to_char(expire at time zone 'UTC', 'YYYYMMDDHH24MI') as utc_expire,
 to_char(issue at time zone 'UTC', 'YYYYMMDDHH24MI') as utc_issue,
 to_char(product_issue at time zone 'UTC', 'YYYYMMDDHH24MI') as utc_prodissue,
 to_char(init_expire at time zone 'UTC', 'YYYYMMDDHH24MI') as utc_init_expire
 from %s w JOIN ugcs u on (u.gid = w.gid) WHERE
 %s %s %s
 )
 SELECT %s from stormbased UNION SELECT %s from countybased %s
""" % (table2, timelimit, wfoLimiter, limiter,
       table1, timelimit, wfoLimiter, limiter,
       cols, cols, sbwlimiter)
# print 'Content-type: text/plain\n'
# print sql
# sys.exit()
data = source.ExecuteSQL(sql)

while True:
    feat = data.GetNextFeature()
    if not feat:
        break

    featDef = ogr.Feature(out_layer.GetLayerDefn())
    featDef.SetGeometry(feat.GetGeometryRef())
    featDef.SetField('ISSUED', feat.GetField("utc_issue"))
    featDef.SetField('EXPIRED', feat.GetField("utc_expire"))
    featDef.SetField('INIT_ISS', feat.GetField("utc_prodissue"))
    featDef.SetField('INIT_EXP', feat.GetField("utc_init_expire"))
    featDef.SetField('PHENOM', feat.GetField("phenomena"))
    featDef.SetField('GTYPE', feat.GetField("gtype"))
    featDef.SetField('SIG', feat.GetField("significance"))
    featDef.SetField('WFO', feat.GetField("wfo"))
    featDef.SetField('ETN', feat.GetField("eventid"))
    featDef.SetField('STATUS', feat.GetField("status"))
    featDef.SetField('NWS_UGC', feat.GetField("ugc"))
    featDef.SetField('AREA_KM2', feat.GetField("area2d"))
    if ((feat.GetField("significance") is None or
            feat.GetField("significance") == "") and
            feat.GetField("phenomena") == 'FF'):
        featDef.SetField('SIG', 'W')
        featDef.SetField('ETN', "-1")
        featDef.SetField('STATUS', "ZZZ")

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

for suffix in ['zip', 'shp', 'shx', 'dbf', 'prj']:
    os.remove("%s.%s" % (fp, suffix))
