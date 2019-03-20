"""Something to dump current warnings to a shapefile."""
from __future__ import print_function
import zipfile
import os
import shutil
import subprocess

from osgeo import ogr
from pyiem.util import utc


def main():
    """Go Main Go"""
    utcnow = utc()

    os.chdir("/tmp")
    fp = "current_ww"
    for suffix in ['shp', 'shx', 'dbf']:
        if os.path.isfile("%s.%s" % (fp, suffix)):
            os.remove("%s.%s" % (fp, suffix))

    source = ogr.Open("PG:host=iemdb dbname=postgis user=nobody")

    out_driver = ogr.GetDriverByName('ESRI Shapefile')
    out_ds = out_driver.CreateDataSource("%s.shp" % (fp, ))
    out_layer = out_ds.CreateLayer("polygon", None, ogr.wkbPolygon)

    fd = ogr.FieldDefn('ISSUED', ogr.OFTString)
    fd.SetWidth(12)
    out_layer.CreateField(fd)

    fd = ogr.FieldDefn('EXPIRED', ogr.OFTString)
    fd.SetWidth(12)
    out_layer.CreateField(fd)

    fd = ogr.FieldDefn('UPDATED', ogr.OFTString)
    fd.SetWidth(12)
    out_layer.CreateField(fd)

    fd = ogr.FieldDefn('INIT_ISS', ogr.OFTString)
    fd.SetWidth(12)
    out_layer.CreateField(fd)

    fd = ogr.FieldDefn('INIT_EXP', ogr.OFTString)
    fd.SetWidth(12)
    out_layer.CreateField(fd)

    fd = ogr.FieldDefn('TYPE', ogr.OFTString)
    fd.SetWidth(2)
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

    fd = ogr.FieldDefn('WFO', ogr.OFTString)
    fd.SetWidth(3)
    out_layer.CreateField(fd)

    fd = ogr.FieldDefn('ETN', ogr.OFTInteger)
    out_layer.CreateField(fd)

    fd = ogr.FieldDefn('STATUS', ogr.OFTString)
    fd.SetWidth(3)
    out_layer.CreateField(fd)

    fd = ogr.FieldDefn('NWS_UGC', ogr.OFTString)
    fd.SetWidth(6)
    out_layer.CreateField(fd)

    sql = """
     SELECT geom, 'P' as gtype, significance, wfo, status, eventid,
     null as ugc, phenomena,
     to_char(expire at time zone 'UTC', 'YYYYMMDDHH24MI') as utcexpire,
     to_char(issue at time zone 'UTC', 'YYYYMMDDHH24MI') as utcissue,
     to_char(polygon_begin at time zone 'UTC', 'YYYYMMDDHH24MI') as utcupdated,
     to_char(issue at time zone 'UTC', 'YYYYMMDDHH24MI') as utc_prodissue,
     to_char(init_expire at time zone 'UTC', 'YYYYMMDDHH24MI')
         as utc_init_expire
     from sbw_%s WHERE polygon_begin <= '%s' and polygon_end > '%s'

    UNION

     SELECT u.simple_geom as geom, 'C' as gtype, significance, w.wfo, status,
     eventid, u.ugc, phenomena,
     to_char(expire at time zone 'UTC', 'YYYYMMDDHH24MI') as utcexpire,
     to_char(issue at time zone 'UTC', 'YYYYMMDDHH24MI') as utcissue,
     to_char(updated at time zone 'UTC', 'YYYYMMDDHH24MI') as utcupdated,
     to_char(product_issue at time zone 'UTC', 'YYYYMMDDHH24MI')
         as utc_prodissue,
     to_char(init_expire at time zone 'UTC', 'YYYYMMDDHH24MI')
         as utc_init_expire
     from warnings_%s w JOIN ugcs u on (u.gid = w.gid) WHERE
     expire > '%s' and w.gid is not null

    """ % (utcnow.year, utcnow, utcnow, utcnow.year, utcnow)

    data = source.ExecuteSQL(sql)

    while True:
        feat = data.GetNextFeature()
        if not feat:
            break
        geom = feat.GetGeometryRef()
        if geom is None:
            continue
        # at 0.001 we had marine zones disappear!
        geom = geom.Simplify(0.0001)

        featDef = ogr.Feature(out_layer.GetLayerDefn())
        featDef.SetGeometry(geom)
        featDef.SetField('GTYPE', feat.GetField("gtype"))
        featDef.SetField('TYPE', feat.GetField("phenomena"))
        featDef.SetField('PHENOM', feat.GetField("phenomena"))
        featDef.SetField('ISSUED', feat.GetField("utcissue"))
        featDef.SetField('EXPIRED', feat.GetField("utcexpire"))
        featDef.SetField('UPDATED', feat.GetField("utcupdated"))
        featDef.SetField('INIT_ISS', feat.GetField("utc_prodissue"))
        featDef.SetField('INIT_EXP', feat.GetField("utc_init_expire"))
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
    shutil.copy('/opt/iem/scripts/GIS/current_ww.shp.xml',
                'current_ww.shp.xml')
    z.write("current_ww.shp.xml")
    z.write("current_ww.shx")
    z.write("current_ww.dbf")
    shutil.copy('/opt/iem/data/gis/meta/4326.prj', 'current_ww.prj')
    z.write("current_ww.prj")
    z.close()

    cmd = ("/home/ldm/bin/pqinsert -p \"zip c %s "
           "gis/shape/4326/us/current_ww.zip bogus zip\" current_ww.zip"
           ) % (utcnow.strftime("%Y%m%d%H%M"),)
    subprocess.call(cmd, shell=True)
    for suffix in ['shp', 'shp.xml', 'shx', 'dbf', 'prj', 'zip']:
        os.remove('current_ww.%s' % (suffix,))


if __name__ == '__main__':
    main()
