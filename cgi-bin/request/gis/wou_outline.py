"""Generate a Watch Outline for a given SPC convective watch """
import zipfile
import os
from io import BytesIO

import shapefile
import psycopg2.extras
from paste.request import parse_formvars
from pyiem import wellknowntext
from pyiem.util import get_dbconn

POSTGIS = get_dbconn("postgis")


def main(year, etn, start_response):
    """Go Main Go"""
    pcursor = POSTGIS.cursor(cursor_factory=psycopg2.extras.DictCursor)

    basefn = "watch_%s_%s" % (year, etn)

    os.chdir("/tmp/")

    sql = """select
        ST_astext(ST_multi(ST_union(ST_SnapToGrid(u.geom,0.0001)))) as tgeom
        from warnings_%s w JOIN ugcs u on (u.gid = w.gid)
        WHERE significance = 'A'
        and phenomena IN ('TO','SV') and eventid = %s and
        ST_isvalid(u.geom)
        and issue < ((select issued from watches WHERE num = %s
        and extract(year from issued) = %s LIMIT 1) + '60 minutes'::interval)
    """ % (
        year,
        etn,
        etn,
        year,
    )
    pcursor.execute(sql)
    if pcursor.rowcount == 0:
        start_response("200 OK", [("Content-type", "text/plain")])
        return b"No Data Found"

    shpio = BytesIO()
    shxio = BytesIO()
    dbfio = BytesIO()
    with shapefile.Writer(shx=shxio, shp=shpio, dbf=dbfio) as shp:
        shp.field("SIG", "C", "1")
        shp.field("ETN", "I", "4")

        row = pcursor.fetchone()
        s = row["tgeom"]
        f = wellknowntext.convert_well_known_text(s)
        shp.poly(f)
        shp.record("A", etn)

    zio = BytesIO()
    with zipfile.ZipFile(
        zio, mode="w", compression=zipfile.ZIP_DEFLATED
    ) as zf:
        zf.writestr(
            basefn + ".prj", open(("/opt/iem/data/gis/meta/4326.prj")).read()
        )
        zf.writestr(basefn + ".shp", shpio.getvalue())
        zf.writestr(basefn + ".shx", shxio.getvalue())
        zf.writestr(basefn + ".dbf", dbfio.getvalue())

    headers = [
        ("Content-type", "application/octet-stream"),
        ("Content-Disposition", "attachment; filename=%s.zip" % (basefn,)),
    ]
    start_response("200 OK", headers)
    return zio.getvalue()


def application(environ, start_response):
    """Yawn"""
    form = parse_formvars(environ)
    year = int(form.get("year", 2018))
    etn = int(form.get("etn", 1))

    return [main(year, etn, start_response)]
