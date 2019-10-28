#!/usr/bin/env python
"""Generate a Watch Outline for a given SPC convective watch """

import zipfile
import os
import sys
import cgi
from io import BytesIO

import shapefile
import psycopg2.extras
from pyiem import wellknowntext
from pyiem.util import get_dbconn, ssw

POSTGIS = get_dbconn("postgis", user="nobody")


def main(year, etn):
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
        sys.exit()

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
    zf = zipfile.ZipFile(zio, mode="w", compression=zipfile.ZIP_DEFLATED)
    zf.writestr(
        basefn + ".prj", open(("/opt/iem/data/gis/meta/4326.prj")).read()
    )
    zf.writestr(basefn + ".shp", shpio.getvalue())
    zf.writestr(basefn + ".shx", shxio.getvalue())
    zf.writestr(basefn + ".dbf", dbfio.getvalue())
    zf.close()
    ssw(("Content-Disposition: attachment; filename=%s.zip\n\n") % (basefn,))
    ssw(zio.getvalue())


def cgiworkflow():
    """Yawn"""
    form = cgi.FieldStorage()
    year = int(form.getfirst("year", 2018))
    etn = int(form.getfirst("etn", 1))

    main(year, etn)


if __name__ == "__main__":
    cgiworkflow()
    # main(2017, 1)
