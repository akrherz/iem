#!/usr/bin/env python
"""
Called from IDEPv2 map application
"""
import cgi
import datetime
import sys
import os
import shapelib
import dbflib
import shutil
import zipfile
from pyiem import wellknowntext
import psycopg2.extras


def do(dt):
    """Generate for a given date """
    dbconn = psycopg2.connect(database='idep', host='iemdb', user='nobody')
    cursor = dbconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("""
    SELECT ST_AsText(i.geom), i.huc_12, coalesce(avg_precip, 0),
    coalesce(avg_loss, 0), coalesce(avg_runoff, 0),
    coalesce(avg_delivery, 0) from ia_huc12 i JOIN results_by_huc12 r
    on (r.huc_12 = i.huc_12) WHERE valid = %s
    """, (dt,))

    os.chdir("/tmp")
    fn = "idepv2_%s" % (dt.strftime("%Y%m%d"),)
    shp = shapelib.create(fn, shapelib.SHPT_POLYGON)

    dbf = dbflib.create(fn)
    dbf.add_field("HUC_12", dbflib.FTString, 12, 0)
    dbf.add_field("PREC_MM", dbflib.FTDouble, 8, 2)
    dbf.add_field("LOS_KGM2", dbflib.FTDouble, 8, 2)
    dbf.add_field("RUNOF_MM", dbflib.FTDouble, 8, 2)
    dbf.add_field("DELI_KGM", dbflib.FTDouble, 8, 2)

    for i, row in enumerate(cursor):
        g = wellknowntext.convert_well_known_text(row[0])
        obj = shapelib.SHPObject(shapelib.SHPT_POLYGON, 1, g)
        shp.write_object(-1, obj)
        del(obj)

        dbf.write_record(i, dict(HUC_12=row[1],
                                 PREC_MM=row[2],
                                 LOS_KGM2=row[3],
                                 RUNOF_MM=row[4],
                                 DELI_KGM=row[5]))

    # hack way to close the files
    del(shp)
    del(dbf)

    shutil.copyfile("/mesonet/www/apps/iemwebsite/data/gis/meta/26915.prj",
                    fn+".prj")
    z = zipfile.ZipFile(fn+".zip", 'w', zipfile.ZIP_DEFLATED)
    suffixes = ['shp', 'shx', 'dbf', 'prj']
    for s in suffixes:
        z.write(fn+"."+s)
    z.close()

    sys.stdout.write("Content-type: application/octet-stream\n")
    sys.stdout.write(("Content-Disposition: attachment; filename=%s.zip\n\n"
                      "") % (fn,))

    sys.stdout.write(file(fn+".zip", 'r').read())

    suffixes.append('zip')
    for s in suffixes:
        os.remove(fn+"."+s)


def main():
    """Generate something nice for the users"""
    form = cgi.FieldStorage()
    dt = datetime.datetime.strptime(form.getfirst('dt'), '%Y-%m-%d')
    do(dt)

if __name__ == '__main__':
    main()
