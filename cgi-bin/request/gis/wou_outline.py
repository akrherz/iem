#!/usr/bin/env python
"""Generate a Watch Outline for a given SPC convective watch """

import zipfile
import os
import shutil
import sys
import cgi
import shapefile
import psycopg2.extras
from pyiem import wellknowntext
from pyiem.util import get_dbconn

POSTGIS = get_dbconn('postgis', user='nobody')


def main(year, etn):
    pcursor = POSTGIS.cursor(cursor_factory=psycopg2.extras.DictCursor)

    basefn = "watch_%s_%s" % (year, etn)

    os.chdir("/tmp/")

    w = shapefile.Writer(shapefile.POLYGON)
    w.field('SIG', 'C', '1')
    w.field('ETN', 'I', '4')

    sql = """select
        ST_astext(ST_multi(ST_union(ST_SnapToGrid(u.geom,0.0001)))) as tgeom
        from warnings_%s w JOIN ugcs u on (u.gid = w.gid)
        WHERE significance = 'A'
        and phenomena IN ('TO','SV') and eventid = %s and
        ST_isvalid(u.geom)
        and issue < ((select issued from watches WHERE num = %s
        and extract(year from issued) = %s LIMIT 1) + '60 minutes'::interval)
    """ % (year, etn, etn, year)
    pcursor.execute(sql)

    if pcursor.rowcount == 0:
        sys.exit()

    row = pcursor.fetchone()
    s = row["tgeom"]
    f = wellknowntext.convert_well_known_text(s)
    w.poly(parts=f)
    w.record('A', etn)
    w.save(basefn)

    # Create zip file, send it back to the clients
    shutil.copyfile("/opt/iem/data/gis/meta/4326.prj", "%s.prj" % (basefn, ))
    z = zipfile.ZipFile(basefn+".zip", 'w', zipfile.ZIP_DEFLATED)
    for suffix in ['shp', 'shx', 'dbf', 'prj']:
        z.write("%s.%s" % (basefn, suffix))
    z.close()

    sys.stdout.write("Content-type: application/octet-stream\n")
    sys.stdout.write(("Content-Disposition: attachment; filename=%s.zip\n\n"
                      ) % (basefn, ))

    sys.stdout.write(file("%s.zip" % (basefn, ), 'r').read())

    for suffix in ['zip', 'shp', 'shx', 'dbf', 'prj']:
        os.remove("%s.%s" % (basefn, suffix))


def cgiworkflow():
    form = cgi.FieldStorage()
    year = int(form.getfirst("year"))
    etn = int(form.getfirst("etn"))

    main(year, etn)


if __name__ == '__main__':
    cgiworkflow()
    # main(2017, 1)
