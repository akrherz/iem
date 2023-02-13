"""Watch by county, a one-off"""
import datetime
import os
import tempfile
import zipfile

from osgeo import ogr
from paste.request import parse_formvars

PROJFILE = "/opt/iem/data/gis/meta/4326.prj"


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
        fp = f"watch_by_county_{ts:%Y%m%d%H%M}"
    else:
        ts = datetime.datetime.utcnow()
        fp = "watch_by_county"

    if "etn" in form:
        etnLimiter = f"and eventid = {int(form.get('etn'))}"
        fp = f"watch_by_county_{ts:Y%m%d%H%M}_{int(form.get('etn'))}"
    else:
        etnLimiter = ""

    with tempfile.TemporaryDirectory() as tempdir:
        os.chdir(tempdir)

        table = f"warnings_{ts.year}"
        source = ogr.Open(
            "PG:host=iemdb-postgis.local dbname=postgis "
            f"user=nobody tables={table}(tgeom)"
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

        fd = ogr.FieldDefn("PHENOM", ogr.OFTString)
        fd.SetWidth(2)
        out_layer.CreateField(fd)

        fd = ogr.FieldDefn("SIG", ogr.OFTString)
        fd.SetWidth(1)
        out_layer.CreateField(fd)

        fd = ogr.FieldDefn("ETN", ogr.OFTInteger)
        out_layer.CreateField(fd)

        tt = ts.strftime("%Y-%m-%d %H:%M+00")
        sql = f"""
            select phenomena, eventid, ST_multi(ST_union(u.geom)) as tgeom,
            max(to_char(expire at time zone 'UTC', 'YYYYMMDDHH24MI'))
                as utcexpire,
            min(to_char(issue at time zone 'UTC', 'YYYYMMDDHH24MI'))
                as utcissue
            from warnings_{ts.year} w JOIN ugcs u on (u.gid = w.gid)
            WHERE significance = 'A' and phenomena IN ('TO','SV')
            and issue > '{tt}'::timestamp -'3 days':: interval
            and issue <= '{tt}' and
            expire > '{tt}' {etnLimiter}
            GROUP by phenomena, eventid ORDER by phenomena ASC
        """

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
        with zipfile.ZipFile(fp + ".zip", "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(fp + ".shp")
            zf.write(fp + ".shx")
            zf.write(fp + ".dbf")
            with open(PROJFILE, encoding="ascii") as fh:
                zf.writestr(f"{fp}.prj", fh.read())
        with open(f"{fp}.zip", "rb") as fh:
            payload = fh.read()

    headers = [
        ("Content-type", "application/octet-stream"),
        ("Content-Disposition", f"attachment; filename={fp}.zip"),
    ]
    start_response("200 OK", headers)
    return [payload]
