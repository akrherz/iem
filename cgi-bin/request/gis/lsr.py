#!/usr/bin/env python
"""
 Dump LSRs to a shapefile
"""
import datetime
import zipfile
import os
import sys
import cgi
from io import BytesIO

import shapefile
from pyiem.util import get_dbconn, ssw


def send_error(msg):
    """Please send an error"""
    ssw("Content-type: text/plain\n\n")
    ssw(msg)
    sys.exit()


def get_time_domain(form):
    """Figure out the start and end timestamps"""
    if 'recent' in form:
        # Allow for specifying a recent number of seconds
        ets = datetime.datetime.utcnow()
        seconds = abs(int(form.getfirst('recent')))
        sts = ets - datetime.timedelta(seconds=seconds)
        return sts, ets

    if 'year' in form:
        year1 = int(form.getfirst("year"))
        year2 = int(form.getfirst("year"))
    else:
        year1 = int(form.getfirst("year1"))
        year2 = int(form.getfirst("year2"))
    month1 = int(form.getfirst("month1"))
    if form.getfirst('month2') is None:
        sys.exit()
    month2 = int(form.getfirst("month2"))
    day1 = int(form.getfirst("day1"))
    day2 = int(form.getfirst("day2"))
    hour1 = int(form.getfirst("hour1"))
    hour2 = int(form.getfirst("hour2"))
    minute1 = int(form.getfirst("minute1"))
    minute2 = int(form.getfirst("minute2"))
    sts = datetime.datetime(year1, month1, day1, hour1, minute1)
    ets = datetime.datetime(year2, month2, day2, hour2, minute2)

    return sts, ets


def main():
    """Go Main Go"""
    if os.environ['REQUEST_METHOD'] == 'OPTIONS':
        ssw("Allow: GET,POST,OPTIONS\n\n")
        sys.exit()

    pgconn = get_dbconn('postgis')
    cursor = pgconn.cursor()

    # Get CGI vars
    form = cgi.FieldStorage()

    (sTS, eTS) = get_time_domain(form)

    wfoLimiter = ""
    if 'wfo[]' in form:
        aWFO = form.getlist('wfo[]')
        aWFO.append('XXX')  # Hack to make next section work
        if "ALL" not in aWFO:
            wfoLimiter = " and wfo in %s " % (str(tuple(aWFO)), )

    os.chdir('/tmp')
    fn = "lsr_%s_%s" % (sTS.strftime("%Y%m%d%H%M"), eTS.strftime("%Y%m%d%H%M"))
    for suffix in ['shp', 'shx', 'dbf', 'csv']:
        if os.path.isfile("%s.%s" % (fn, suffix)):
            os.remove("%s.%s" % (fn, suffix))

    csv = open("%s.csv" % (fn,), 'w')
    csv.write(("VALID,VALID2,LAT,LON,MAG,WFO,TYPECODE,TYPETEXT,CITY,"
               "COUNTY,STATE,SOURCE,REMARK\n"))

    cursor.execute("""
        SELECT distinct
        to_char(valid at time zone 'UTC', 'YYYYMMDDHH24MI') as dvalid,
        magnitude, wfo, type, typetext,
        city, county, state, source, substr(remark,0,200) as tremark,
        ST_y(geom), ST_x(geom),
        to_char(valid at time zone 'UTC', 'YYYY/MM/DD HH24:MI') as dvalid2
        from lsrs WHERE
        valid >= '%s+00' and valid < '%s+00' %s
        ORDER by dvalid ASC
        """ % (sTS.strftime("%Y-%m-%d %H:%M"),
               eTS.strftime("%Y-%m-%d %H:%M"), wfoLimiter))

    if cursor.rowcount == 0:
        send_error("ERROR: No results found for query.")

    shpio = BytesIO()
    shxio = BytesIO()
    dbfio = BytesIO()

    with shapefile.Writer(shp=shpio, shx=shxio, dbf=dbfio) as shp:
        shp.field('VALID', 'C', 12)
        shp.field('MAG', 'F', 5, 2)
        shp.field('WFO', 'C', 3)
        shp.field('TYPECODE', 'C', 1)
        shp.field('TYPETEXT', 'C', 40)
        shp.field('CITY', 'C', 40)
        shp.field('COUNTY', 'C', 40)
        shp.field('STATE', 'C', 2)
        shp.field('SOURCE', 'C', 40)
        shp.field('REMARK', 'C', 200)
        shp.field('LAT', 'F', 7, 4)
        shp.field('LON', 'F', 9, 4)
        for row in cursor:
            row = list(row)
            shp.point(row[-2], row[-3])
            if row[9] is not None:
                row[9] = row[9].encode('utf-8', 'ignore').decode(
                                'ascii', 'ignore').replace(",", "_")
            shp.record(*row[:-1])
            csv.write(
                ("%s,%s,%.2f,%.2f,%s,%s,%s,%s,%s,%s,%s,%s,%s\n"
                 ) % (row[0], row[12], row[-3], row[-2], row[1], row[2],
                      row[3],
                      row[4], row[5].encode(
                        'utf-8', 'ignore').decode('ascii', 'ignore'),
                      row[6], row[7], row[8],
                      row[9] if row[9] is not None else ''))

    csv.close()

    zio = BytesIO()
    zf = zipfile.ZipFile(zio, mode='w',
                         compression=zipfile.ZIP_DEFLATED)
    zf.writestr(fn+'.prj',
                open(('/opt/iem/data/gis/meta/4326.prj'
                      )).read())
    zf.writestr(fn+".shp", shpio.getvalue())
    zf.writestr(fn+'.shx', shxio.getvalue())
    zf.writestr(fn+'.dbf', dbfio.getvalue())
    zf.writestr(fn+'.csv', open(fn+'.csv', 'r').read())
    zf.close()

    if "justcsv" in form:
        ssw("Content-type: application/octet-stream\n")
        ssw(("Content-Disposition: "
             "attachment; filename=%s.csv\n\n") % (fn,))
        ssw(open(fn+".csv", 'r').read())

    else:
        ssw(("Content-Disposition: attachment; "
             "filename=%s.zip\n\n") % (fn,))
        ssw(zio.getvalue())

    os.remove(fn+".csv")


if __name__ == '__main__':
    main()
