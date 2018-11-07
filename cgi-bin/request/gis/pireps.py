#!/usr/bin/env python
"""
    Dump PIREPs
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

    fmt = form.getfirst('fmt', 'shp')

    return dict(sts=sts, ets=ets, fmt=fmt)


def run(ctx):
    """Go run!"""
    pgconn = get_dbconn('postgis', user='nobody')
    cursor = pgconn.cursor()

    if (ctx['ets'] - ctx['sts']).days > 120:
        ctx['ets'] = ctx['sts'] + datetime.timedelta(days=120)

    sql = """
        SELECT to_char(valid at time zone 'UTC', 'YYYYMMDDHH24MI') as utctime,
        case when is_urgent then 'T' else 'F' end,
        substr(aircraft_type, 0, 40), substr(report, 0, 255),
        ST_y(geom::geometry) as lat, ST_x(geom::geometry) as lon
        from pireps WHERE
        valid >= '%s' and valid < '%s'  ORDER by valid ASC
        """ % (ctx['sts'].strftime("%Y-%m-%d %H:%M+00"),
               ctx['ets'].strftime("%Y-%m-%d %H:%M+00"))

    cursor.execute(sql)
    if cursor.rowcount == 0:
        ssw("Content-type: text/plain\n\n")
        ssw("ERROR: no results found for your query")
        return

    fn = "pireps_%s_%s" % (ctx['sts'].strftime("%Y%m%d%H%M"),
                           ctx['ets'].strftime("%Y%m%d%H%M"))

    # sys.stderr.write("End SQL with rowcount %s" % (cursor.rowcount, ))
    if ctx['fmt'] == 'csv':
        ssw("Content-type: application/octet-stream\n")
        ssw(("Content-Disposition: attachment; "
             "filename=%s.csv\n\n") % (fn,))
        ssw(("VALID,URGENT,AIRCRAFT,REPORT,LAT,LON\n"))
        for row in cursor:
            ssw(",".join([str(s) for s in row])+"\n")
        return

    shpio = BytesIO()
    shxio = BytesIO()
    dbfio = BytesIO()

    with shapefile.Writer(shx=shxio, dbf=dbfio, shp=shpio) as shp:
        shp.field('VALID', 'C', 12)
        shp.field('URGENT', 'C', 1)
        shp.field('AIRCRAFT', 'C', 40)
        shp.field('REPORT', 'C', 255)  # Max field size is 255
        shp.field('LAT', 'F', 7, 4)
        shp.field('LON', 'F', 9, 4)
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
