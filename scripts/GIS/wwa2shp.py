"""Something to dump current warnings to a shapefile."""

import os
import subprocess
import tempfile
import zipfile

from osgeo import ogr
from pyiem.util import utc

ogr.UseExceptions()
PRJFILE = "/opt/iem/data/gis/meta/4326.prj"
XMLFILE = "/opt/iem/scripts/GIS/current_ww.shp.xml"


def workflow():
    """Do work."""
    utcnow = utc()
    fp = "current_ww"
    source = ogr.Open(
        "PG:host=iemdb-postgis.local dbname=postgis gssencmode=disable"
    )

    out_driver = ogr.GetDriverByName("ESRI Shapefile")
    out_ds = out_driver.CreateDataSource(f"{fp}.shp")
    out_layer = out_ds.CreateLayer("polygon", None, ogr.wkbPolygon)

    fd = ogr.FieldDefn("ISSUED", ogr.OFTString)
    fd.SetWidth(12)
    out_layer.CreateField(fd)

    fd = ogr.FieldDefn("EXPIRED", ogr.OFTString)
    fd.SetWidth(12)
    out_layer.CreateField(fd)

    fd = ogr.FieldDefn("UPDATED", ogr.OFTString)
    fd.SetWidth(12)
    out_layer.CreateField(fd)

    fd = ogr.FieldDefn("INIT_ISS", ogr.OFTString)
    fd.SetWidth(12)
    out_layer.CreateField(fd)

    fd = ogr.FieldDefn("INIT_EXP", ogr.OFTString)
    fd.SetWidth(12)
    out_layer.CreateField(fd)

    fd = ogr.FieldDefn("TYPE", ogr.OFTString)
    fd.SetWidth(2)
    out_layer.CreateField(fd)

    fd = ogr.FieldDefn("PHENOM", ogr.OFTString)
    fd.SetWidth(2)
    out_layer.CreateField(fd)

    fd = ogr.FieldDefn("GTYPE", ogr.OFTString)
    fd.SetWidth(1)
    out_layer.CreateField(fd)

    fd = ogr.FieldDefn("SIG", ogr.OFTString)
    fd.SetWidth(1)
    out_layer.CreateField(fd)

    fd = ogr.FieldDefn("WFO", ogr.OFTString)
    fd.SetWidth(3)
    out_layer.CreateField(fd)

    fd = ogr.FieldDefn("ETN", ogr.OFTInteger)
    out_layer.CreateField(fd)

    fd = ogr.FieldDefn("STATUS", ogr.OFTString)
    fd.SetWidth(3)
    out_layer.CreateField(fd)

    fd = ogr.FieldDefn("NWS_UGC", ogr.OFTString)
    fd.SetWidth(6)
    out_layer.CreateField(fd)

    fd = ogr.FieldDefn("FL_NWSLI", ogr.OFTString)
    fd.SetWidth(5)
    out_layer.CreateField(fd)

    sql = f"""
     SELECT geom, 'P' as gtype, significance, wfo, status, eventid,
     null as ugc, phenomena,
     to_char(expire at time zone 'UTC', 'YYYYMMDDHH24MI') as utcexpire,
     to_char(issue at time zone 'UTC', 'YYYYMMDDHH24MI') as utcissue,
     to_char(polygon_begin at time zone 'UTC', 'YYYYMMDDHH24MI') as utcupdated,
     to_char(issue at time zone 'UTC', 'YYYYMMDDHH24MI') as utc_prodissue,
     to_char(init_expire at time zone 'UTC', 'YYYYMMDDHH24MI')
         as utc_init_expire,
     hvtec_nwsli
     from sbw_{utcnow.year} WHERE
     polygon_begin <= '{utcnow}' and polygon_end > '{utcnow}'

    UNION

     SELECT u.simple_geom as geom, 'C' as gtype, significance, w.wfo, status,
     eventid, u.ugc, phenomena,
     to_char(expire at time zone 'UTC', 'YYYYMMDDHH24MI') as utcexpire,
     to_char(issue at time zone 'UTC', 'YYYYMMDDHH24MI') as utcissue,
     to_char(updated at time zone 'UTC', 'YYYYMMDDHH24MI') as utcupdated,
     to_char(product_issue at time zone 'UTC', 'YYYYMMDDHH24MI')
         as utc_prodissue,
     to_char(init_expire at time zone 'UTC', 'YYYYMMDDHH24MI')
         as utc_init_expire,
     hvtec_nwsli
     from warnings_{utcnow.year} w JOIN ugcs u on (u.gid = w.gid) WHERE
     expire > '{utcnow}' and w.gid is not null
    """

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
        featDef.SetField("GTYPE", feat.GetField("gtype"))
        featDef.SetField("TYPE", feat.GetField("phenomena"))
        featDef.SetField("PHENOM", feat.GetField("phenomena"))
        featDef.SetField("ISSUED", feat.GetField("utcissue"))
        featDef.SetField("EXPIRED", feat.GetField("utcexpire"))
        featDef.SetField("UPDATED", feat.GetField("utcupdated"))
        featDef.SetField("INIT_ISS", feat.GetField("utc_prodissue"))
        featDef.SetField("INIT_EXP", feat.GetField("utc_init_expire"))
        featDef.SetField("SIG", feat.GetField("significance"))
        featDef.SetField("WFO", feat.GetField("wfo"))
        featDef.SetField("STATUS", feat.GetField("status"))
        featDef.SetField("ETN", feat.GetField("eventid"))
        featDef.SetField("NWS_UGC", feat.GetField("ugc"))
        featDef.SetField("FL_NWSLI", feat.GetField("hvtec_nwsli"))

        out_layer.CreateFeature(featDef)
        feat.Destroy()

    source.Destroy()
    out_ds.Destroy()

    with zipfile.ZipFile("current_ww.zip", "w", zipfile.ZIP_DEFLATED) as z:
        z.write("current_ww.shp")
        with open(XMLFILE, encoding="ascii") as fh:
            z.writestr("current_ww.shp.xml", fh.read())
        z.write("current_ww.shx")
        z.write("current_ww.dbf")
        with open(PRJFILE, encoding="ascii") as fh:
            z.writestr("current_ww.prj", fh.read())

    cmd = [
        "pqinsert",
        "-p",
        (
            f"zip c {utcnow:%Y%m%d%H%M} gis/shape/4326/us/current_ww.zip "
            "bogus zip"
        ),
        "current_ww.zip",
    ]
    subprocess.call(cmd)


def main():
    """Go Main Go"""
    with tempfile.TemporaryDirectory() as tempdir:
        os.chdir(tempdir)
        workflow()


if __name__ == "__main__":
    main()
