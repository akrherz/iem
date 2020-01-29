"""Watch by county, a one-off"""

import zipfile
import os
import shutil
import datetime

from osgeo import ogr
from paste.request import parse_formvars


def application(environ, start_response):
    """Go Main Go"""
    # Get CGI vars
    form = parse_formvars(environ)
    if "year" in form:
        year = int(form.get("year"))
        month = int(form.get("month"))
        day = int(form.get("day"))
        hour = int(form.get("hour"))
        minute = int(form.get("minute"))
        ts = datetime.datetime(year, month, day, hour, minute)
        fp = "watch_by_county_%s" % (ts.strftime("%Y%m%d%H%M"),)
    else:
        ts = datetime.datetime.utcnow()
        fp = "watch_by_county"

    if "etn" in form:
        etnLimiter = "and eventid = %s" % (int(form.get("etn")),)
        fp = "watch_by_county_%s_%s" % (
            ts.strftime("%Y%m%d%H%M"),
            int(form.get("etn")),
        )
    else:
        etnLimiter = ""

    os.chdir("/tmp/")
    for suffix in ["shp", "shx", "dbf"]:
        if os.path.isfile("%s.%s" % (fp, suffix)):
            os.remove("%s.%s" % (fp, suffix))

    table = "warnings_%s" % (ts.year,)
    source = ogr.Open(
        (
            "PG:host=iemdb-postgis.local dbname=postgis "
            "user=nobody tables=%s(tgeom)"
        )
        % (table,)
    )

    out_driver = ogr.GetDriverByName("ESRI Shapefile")
    out_ds = out_driver.CreateDataSource("%s.shp" % (fp,))
    out_layer = out_ds.CreateLayer("polygon", None, ogr.wkbPolygon)

    fd = ogr.FieldDefn("ISSUED", ogr.OFTString)
    fd.SetWidth(12)
    out_layer.CreateField(fd)

    fd = ogr.FieldDefn("EXPIRED", ogr.OFTString)
    fd.SetWidth(12)
    out_layer.CreateField(fd)

    fd = ogr.FieldDefn("PHENOM", ogr.OFTString)
    fd.SetWidth(2)
    out_layer.CreateField(fd)

    fd = ogr.FieldDefn("SIG", ogr.OFTString)
    fd.SetWidth(1)
    out_layer.CreateField(fd)

    fd = ogr.FieldDefn("ETN", ogr.OFTInteger)
    out_layer.CreateField(fd)

    sql = """
        select phenomena, eventid, ST_multi(ST_union(u.geom)) as tgeom,
        max(to_char(expire at time zone 'UTC', 'YYYYMMDDHH24MI')) as utcexpire,
        min(to_char(issue at time zone 'UTC', 'YYYYMMDDHH24MI')) as utcissue
        from warnings_%s w JOIN ugcs u on (u.gid = w.gid)
        WHERE significance = 'A' and phenomena IN ('TO','SV')
        and issue > '%s'::timestamp -'3 days':: interval
        and issue <= '%s' and
        expire > '%s' %s GROUP by phenomena, eventid ORDER by phenomena ASC
    """ % (
        ts.year,
        ts.strftime("%Y-%m-%d %H:%M+00"),
        ts.strftime("%Y-%m-%d %H:%M+00"),
        ts.strftime("%Y-%m-%d %H:%M+00"),
        etnLimiter,
    )

    data = source.ExecuteSQL(sql)

    while True:
        feat = data.GetNextFeature()
        if not feat:
            break
        geom = feat.GetGeometryRef()

        featDef = ogr.Feature(out_layer.GetLayerDefn())
        featDef.SetGeometry(geom)
        featDef.SetField("PHENOM", feat.GetField("phenomena"))
        featDef.SetField("SIG", "A")
        featDef.SetField("ETN", feat.GetField("eventid"))
        featDef.SetField("ISSUED", feat.GetField("utcissue"))
        featDef.SetField("EXPIRED", feat.GetField("utcexpire"))

        out_layer.CreateFeature(featDef)
        feat.Destroy()

    source.Destroy()
    out_ds.Destroy()

    # Create zip file, send it back to the clients
    shutil.copyfile("/opt/iem/data/gis/meta/4326.prj", fp + ".prj")
    with zipfile.ZipFile(fp + ".zip", "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(fp + ".shp")
        zf.write(fp + ".shx")
        zf.write(fp + ".dbf")
        zf.write(fp + ".prj")

    headers = [
        ("Content-type", "application/octet-stream"),
        ("Content-Disposition", "attachment; filename=%s.zip" % (fp,)),
    ]
    start_response("200 OK", headers)
    payload = open(fp + ".zip", "rb").read()

    for suffix in ["zip", "shp", "shx", "dbf", "prj"]:
        os.remove("%s.%s" % (fp, suffix))
    return [payload]
