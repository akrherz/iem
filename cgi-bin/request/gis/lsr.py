#!/usr/bin/python
"""
 Dump LSRs to a shapefile
"""
import datetime
import zipfile
import os
import sys
import cgi
import StringIO

import shapefile
import psycopg2


def send_error(msg):
    """Please send an error"""
    sys.stdout.write("Content-type: text/plain\n\n")
    sys.stdout.write(msg)
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
        sys.stdout.write("Allow: GET,POST,OPTIONS\n\n")
        sys.exit()

    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
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
        city, county, state, source, substr(remark,0,100) as tremark,
        ST_y(geom), ST_x(geom),
        to_char(valid at time zone 'UTC', 'YYYY/MM/DD HH24:MI') as dvalid2
        from lsrs WHERE
        valid >= '%s+00' and valid < '%s+00' %s
        ORDER by dvalid ASC
        """ % (sTS.strftime("%Y-%m-%d %H:%M"),
               eTS.strftime("%Y-%m-%d %H:%M"), wfoLimiter))

    if cursor.rowcount == 0:
        send_error("ERROR: No results found for query.")

    w = shapefile.Writer(shapeType=shapefile.POINT)
    w.field('VALID', 'C', 12)
    w.field('MAG', 'F', 5, 2)
    w.field('WFO', 'C', 3)
    w.field('TYPECODE', 'C', 1)
    w.field('TYPETEXT', 'C', 40)
    w.field('CITY', 'C', 40)
    w.field('COUNTY', 'C', 40)
    w.field('STATE', 'C', 2)
    w.field('SOURCE', 'C', 40)
    w.field('REMARK', 'C', 100)
    w.field('LAT', 'F', 7, 4)
    w.field('LON', 'F', 9, 4)
    for row in cursor:
        w.point(row[-2], row[-3])
        w.record(*row[:-1])
        csv.write(("%s,%s,%.2f,%.2f,%s,%s,%s,%s,%s,%s,%s,%s,%s\n"
                   ) % (row[0], row[12], row[-3], row[-2], row[1], row[2],
                        row[3],
                        row[4], row[5], row[6], row[7], row[8],
                        row[9].replace(",", "_")
                        if row[9] is not None else ''))

    csv.close()

    shp = StringIO.StringIO()
    shx = StringIO.StringIO()
    dbf = StringIO.StringIO()

    w.save(shp=shp, shx=shx, dbf=dbf)

    zio = StringIO.StringIO()
    zf = zipfile.ZipFile(zio, mode='w',
                         compression=zipfile.ZIP_DEFLATED)
    zf.writestr(fn+'.prj',
                open(('/opt/iem/data/gis/meta/4326.prj'
                      )).read())
    zf.writestr(fn+".shp", shp.getvalue())
    zf.writestr(fn+'.shx', shx.getvalue())
    zf.writestr(fn+'.dbf', dbf.getvalue())
    zf.writestr(fn+'.csv', open(fn+'.csv', 'r').read())
    zf.close()

    if "justcsv" in form:
        sys.stdout.write("Content-type: application/octet-stream\n")
        sys.stdout.write(("Content-Disposition: "
                          "attachment; filename=%s.csv\n\n"
                          ) % (fn,))
        sys.stdout.write(open(fn+".csv", 'r').read())

    else:
        sys.stdout.write(("Content-Disposition: attachment; "
                          "filename=%s.zip\n\n") % (fn,))
        sys.stdout.write(zio.getvalue())

    os.remove(fn+".csv")


if __name__ == '__main__':
    main()
