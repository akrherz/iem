#!/usr/bin/env python
"""
    Dump storm attributes from the database to a shapefile for the users
"""
import datetime
import zipfile
import cgi
from io import BytesIO
# import cgitb
import shapefile
from pyiem.util import get_dbconn, utc, ssw
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

    sts = utc(int(year1), int(month1), int(day1),
              int(hour1), int(minute1))
    ets = utc(int(year2), int(month2), int(day2),
              int(hour2), int(minute2))
    if ets < sts:
        s = ets
        ets = sts
        sts = s
    radar = form.getlist('radar')

    fmt = form.getfirst('fmt', 'shp')

    return dict(sts=sts, ets=ets, radar=radar, fmt=fmt)


def run(ctx):
    """Do something!"""
    pgconn = get_dbconn('postgis', user='nobody')
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
        ssw("Content-type: text/plain\n\n")
        ssw("ERROR: no results found for your query")
        return

    fn = "stormattr_%s_%s" % (ctx['sts'].strftime("%Y%m%d%H%M"),
                              ctx['ets'].strftime("%Y%m%d%H%M"))

    # sys.stderr.write("End SQL with rowcount %s" % (cursor.rowcount, ))
    if ctx['fmt'] == 'csv':
        ssw("Content-type: application/octet-stream\n")
        ssw(("Content-Disposition: attachment; "
             "filename=%s.csv\n\n") % (fn,))
        ssw(("VALID,STORM_ID,NEXRAD,AZIMUTH,RANGE,TVS,MESO,POSH,"
             "POH,MAX_SIZE,VIL,MAX_DBZ,MAZ_DBZ_H,TOP,DRCT,SKNT,LAT,LON\n"))
        for row in cursor:
            ssw(",".join([str(s) for s in row])+"\n")
        return

    shpio = BytesIO()
    shxio = BytesIO()
    dbfio = BytesIO()

    with shapefile.Writer(shp=shpio, shx=shxio, dbf=dbfio) as shp:
        """
C is ASCII characters
N is a double precision integer limited to around 18 characters in length
D is for dates in the YYYYMMDD format,
     with no spaces or hyphens between the sections
F is for floating point numbers with the same length limits as N
L is for logical data which is stored in the shapefile's attribute table as a
    short integer as a 1 (true) or a 0 (false).
    The values it can receive are 1, 0, y, n, Y, N, T, F
    or the python builtins True and False
        """
        shp.field('VALID', 'C', 12)
        shp.field('STORM_ID', 'C', 2)
        shp.field('NEXRAD', 'C', 3)
        shp.field('AZIMUTH', 'N', 3, 0)
        shp.field('RANGE', 'N', 3, 0)
        shp.field('TVS', 'C', 10)
        shp.field('MESO', 'C', 10)
        shp.field('POSH', 'N', 3, 0)
        shp.field('POH', 'N', 3, 0)
        shp.field('MAX_SIZE', 'F', 5, 2)
        shp.field('VIL', 'N', 3, 0)
        shp.field('MAX_DBZ', 'N', 3, 0)
        shp.field('MAX_DBZ_H', 'F', 5, 2)
        shp.field('TOP', 'F', 9, 2)
        shp.field('DRCT', 'N', 3, 0)
        shp.field('SKNT', 'N', 3, 0)
        shp.field('LAT', 'F', 10, 4)
        shp.field('LON', 'F', 10, 4)
        for row in cursor:
            shp.point(row[-1], row[-2])
            shp.record(*row)

    zio = BytesIO()
    zf = zipfile.ZipFile(zio, mode='w',
                         compression=zipfile.ZIP_DEFLATED)
    zf.writestr(fn+'.prj',
                open(('/opt/iem/data/gis/meta/4326.prj'
                      )).read())
    zf.writestr(fn+".shp", shpio.getvalue())
    zf.writestr(fn+'.shx', shxio.getvalue())
    zf.writestr(fn+'.dbf', dbfio.getvalue())
    zf.close()
    ssw(("Content-Disposition: attachment; filename=%s.zip\n\n") % (fn,))
    ssw(zio.getvalue())


def main():
    """Do something fun!"""
    ctx = get_context()
    run(ctx)


if __name__ == '__main__':
    # Go Main!
    main()
