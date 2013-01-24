""" 
Something to dump current warnings to a shapefile
"""
from osgeo import ogr
import zipfile
import os
import datetime
import shutil
import subprocess

now = datetime.datetime.now() + datetime.timedelta(minutes=1)
table = "warnings_%s" % (now.year, )

os.chdir("/tmp")
fp = "current_ww"
for suffix in ['shp', 'shx', 'dbf']:
	if os.path.isfile("%s.%s" % (fp, suffix)):
		os.remove("%s.%s" % (fp, suffix))

source = ogr.Open("PG:host=iemdb dbname=postgis user=nobody tables=%s(geom)" % (
																table,))

out_driver = ogr.GetDriverByName( 'ESRI Shapefile' )
out_ds = out_driver.CreateDataSource("%s.shp" % (fp, ))
out_layer = out_ds.CreateLayer("polygon", None, ogr.wkbPolygon)

fd = ogr.FieldDefn('ISSUED',ogr.OFTString)
fd.SetWidth(12)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('EXPIRED',ogr.OFTString)
fd.SetWidth(12)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('UPDATED',ogr.OFTString)
fd.SetWidth(12)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('TYPE',ogr.OFTString)
fd.SetWidth(2)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('GTYPE',ogr.OFTString)
fd.SetWidth(1)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('SIG',ogr.OFTString)
fd.SetWidth(1)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('WFO',ogr.OFTString)
fd.SetWidth(3)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('ETN',ogr.OFTInteger)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('STATUS',ogr.OFTString)
fd.SetWidth(3)
out_layer.CreateField(fd)

fd = ogr.FieldDefn('NWS_UGC',ogr.OFTString)
fd.SetWidth(6)
out_layer.CreateField(fd)


#pcursor = POSTGIS.cursor(cursor_factory=psycopg2.extras.DictCursor)
#pcursor.execute("SET TIME ZONE 'GMT'")
# Don't print out annonying errors about ST_IsValid failures
#pcursor.execute("set client_min_messages = ERROR")


sql = """SELECT geom, gtype, significance, wfo,
	status, eventid, ugc, phenomena,
	to_char(expire at time zone 'UTC', 'YYYYMMDDHH24MI') as utcexpire,
	to_char(issue at time zone 'UTC', 'YYYYMMDDHH24MI') as utcissue,
	to_char(updated at time zone 'UTC', 'YYYYMMDDHH24MI') as utcupdated
	from %s 
	WHERE expire > '%s' and ((gtype = 'P' and ST_IsValid(geom)) or gtype = 'C') 
	ORDER by type ASC""" % (table, now.strftime("%Y-%m-%d %H:%M"))

data = source.ExecuteSQL(sql)

while True:
	feat = data.GetNextFeature()
	if not feat:
		break
	geom = feat.GetGeometryRef()
	geom = geom.Simplify(0.001)

	featDef = ogr.Feature(out_layer.GetLayerDefn())
	featDef.SetGeometry( geom )
	featDef.SetField('GTYPE', feat.GetField("gtype"))
	featDef.SetField('TYPE', feat.GetField("phenomena"))
	featDef.SetField('ISSUED', feat.GetField("utcissue"))
	featDef.SetField('EXPIRED', feat.GetField("utcexpire"))
	featDef.SetField('UPDATED', feat.GetField("utcupdated"))
	featDef.SetField('SIG', feat.GetField("significance"))
	featDef.SetField('WFO', feat.GetField("wfo"))
	featDef.SetField('STATUS', feat.GetField("status"))
	featDef.SetField('ETN', feat.GetField("eventid"))
	featDef.SetField('NWS_UGC', feat.GetField("ugc"))

	out_layer.CreateFeature(featDef)
	feat.Destroy()

source.Destroy()
out_ds.Destroy()


z = zipfile.ZipFile("current_ww.zip", 'w', zipfile.ZIP_DEFLATED)
z.write("current_ww.shp")
shutil.copy('/mesonet/www/apps/iemwebsite/scripts/GIS/current_ww.shp.xml', 'current_ww.shp.xml')
z.write("current_ww.shp.xml")
z.write("current_ww.shx")
z.write("current_ww.dbf")
shutil.copy('/mesonet/data/gis/meta/4326.prj', 'current_ww.prj')
z.write("current_ww.prj")
z.close()

cmd = "/home/ldm/bin/pqinsert -p \"zip c %s gis/shape/4326/us/current_ww.zip bogus zip\" current_ww.zip" % (
										now.strftime("%Y%m%d%H%M"),)
subprocess.call(cmd, shell=True)
for suffix in ['shp', 'shp.xml', 'shx', 'dbf', 'prj', 'zip']:
	os.remove('current_ww.%s' % (suffix,))
