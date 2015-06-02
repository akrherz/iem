#!/usr/bin/python
"""
    Dump storm attributes from the database to a shapefile for the users
"""
import datetime
import zipfile
import sys
import cgi
# import cgitb
import psycopg2
import shapefile
import pytz
import cStringIO
# cgitb.enable()


def get_context():
    """Figure out the CGI variables passed to this script"""
    form = cgi.FieldStorage()
    if 'year' in form:
        year1 = form.getfirst('year')
        year2 = year1
    else:
        year1 = form.getfirst('year1')
        year2 = form.getfirst('year2')
    month1 = form.getfirst('month1')
    month2 = form.getfirst('month2')
    day1 = form.getfirst('day1')
    day2 = form.getfirst('day2')
    hour1 = form.getfirst('hour1')
    hour2 = form.getfirst('hour2')
    minute1 = form.getfirst('minute1')
    minute2 = form.getfirst('minute2')

    sts = datetime.datetime(int(year1), int(month1), int(day1),
                            int(hour1), int(minute1))
    sts = sts.replace(tzinfo=pytz.timezone("UTC"))
    ets = datetime.datetime(int(year2), int(month2), int(day2),
                            int(hour2), int(minute2))
    ets = ets.replace(tzinfo=pytz.timezone("UTC"))
    if ets < sts:
        s = ets
        ets = sts
        sts = s
    radar = form.getlist('radar')

    fmt = form.getfirst('fmt', 'shp')

    return dict(sts=sts, ets=ets, radar=radar, fmt=fmt)


def run(ctx):
    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
    cursor = pgconn.cursor()

    """
    Need to limit what we are allowing them to request as the file would get
    massive.  So lets set arbitrary values of
    1) If 2 or more RADARs, less than 7 days
    """
    if len(ctx['radar']) == 1:
        ctx['radar'].append('XXX')
    radarlimit = ''
    if 'ALL' not in ctx['radar']:
            radarlimit = " and nexrad in %s " % (str(tuple(ctx['radar'])), )
    if len(ctx['radar']) > 2 and (ctx['ets'] - ctx['sts']).days > 6:
        ctx['ets'] = ctx['sts'] + datetime.timedelta(days=7)

    sql = """
        SELECT to_char(valid at time zone 'UTC', 'YYYYMMDDHH24MI') as utctime,
        storm_id, nexrad, azimuth, range, tvs, meso, posh, poh, max_size,
        vil, max_dbz, max_dbz_height, top, drct, sknt,
        ST_y(geom) as lat, ST_x(geom) as lon
        from nexrad_attributes_log WHERE
        valid >= '%s' and valid < '%s' %s  ORDER by valid ASC
        """ % (ctx['sts'].strftime("%Y-%m-%d %H:%M+00"),
               ctx['ets'].strftime("%Y-%m-%d %H:%M+00"), radarlimit)

    # print 'Content-type: text/plain\n'
    # print sql
    # sys.exit()
    # sys.stderr.write("Begin SQL...")
    cursor.execute(sql)
    if cursor.rowcount == 0:
        sys.stdout.write("Content-type: text/plain\n\n")
        sys.stdout.write("ERROR: no results found for your query")
        return

    fn = "stormattr_%s_%s" % (ctx['sts'].strftime("%Y%m%d%H%M"),
                              ctx['ets'].strftime("%Y%m%d%H%M"))

    # sys.stderr.write("End SQL with rowcount %s" % (cursor.rowcount, ))
    if ctx['fmt'] == 'csv':
        sys.stdout.write("Content-type: application/octet-stream\n")
        sys.stdout.write(("Content-Disposition: attachment; "
                          "filename=%s.csv\n\n") % (fn,))
        sys.stdout.write(("VALID,STORM_ID,NEXRAD,AZIMUTH,RANGE,TVS,MESO,POSH,"
                          "POH,MAX_SIZE,VIL,MAX_DBZ,MAZ_DBZ_H,TOP,DRCT,SKNT,"
                          "LAT,LON\n"))
        for row in cursor:
            sys.stdout.write(",".join([str(s) for s in row])+"\n")
        return

    w = shapefile.Writer(shapeType=shapefile.POINT)
    w.field('VALID', 'C', 12)
    w.field('STORM_ID', 'C', 2)
    w.field('NEXRAD', 'C', 3)
    w.field('AZIMUTH', 'I')
    w.field('RANGE', 'I')
    w.field('TVS', 'C', 10)
    w.field('MESO', 'C', 10)
    w.field('POSH', 'I')
    w.field('POH', 'I')
    w.field('MAX_SIZE', 'F', 5, 2)
    w.field('VIL', 'I')
    w.field('MAX_DBZ', 'I')
    w.field('MAX_DBZ_H', 'F', 5, 2)
    w.field('TOP', 'F', 5, 2)
    w.field('DRCT', 'I')
    w.field('SKNT', 'I')
    w.field('LAT', 'F', 7, 4)
    w.field('LON', 'F', 9, 4)
    for row in cursor:
        w.point(row[-1], row[-2])
        w.record(*row)

    # sys.stderr.write("End LOOP...")

    shp = cStringIO.StringIO()
    shx = cStringIO.StringIO()
    dbf = cStringIO.StringIO()

    w.save(shp=shp, shx=shx, dbf=dbf)
    # sys.stderr.write("End of w.save()")

    zio = cStringIO.StringIO()
    zf = zipfile.ZipFile(zio, mode='w',
                         compression=zipfile.ZIP_DEFLATED)
    zf.writestr(fn+'.prj',
                open(('/mesonet/www/apps/iemwebsite/data/gis/meta/4326.prj'
                      )).read())
    zf.writestr(fn+".shp", shp.getvalue())
    zf.writestr(fn+'.shx', shx.getvalue())
    zf.writestr(fn+'.dbf', dbf.getvalue())
    zf.close()
    sys.stdout.write(("Content-Disposition: attachment; "
                      "filename=%s.zip\n\n") % (fn,))
    sys.stdout.write(zio.getvalue())


def main():
    """Do something fun!"""
    ctx = get_context()
    run(ctx)
if __name__ == '__main__':
    # Go Main!
    main()
