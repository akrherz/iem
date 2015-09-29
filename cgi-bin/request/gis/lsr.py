#!/usr/bin/python
"""
 Dump LSRs to a shapefile
"""
import datetime
import zipfile
import os
import sys
import cgi
import shapefile
import psycopg2
import cStringIO

pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
cursor = pgconn.cursor()

# Get CGI vars
form = cgi.FormContent()

if 'year' in form:
    year1 = int(form["year"][0])
    year2 = int(form["year"][0])
else:
    year1 = int(form["year1"][0])
    year2 = int(form["year2"][0])
month1 = int(form["month1"][0])
if 'month2' not in form:
    sys.exit()
month2 = int(form["month2"][0])
day1 = int(form["day1"][0])
day2 = int(form["day2"][0])
hour1 = int(form["hour1"][0])
hour2 = int(form["hour2"][0])
minute1 = int(form["minute1"][0])
minute2 = int(form["minute2"][0])

wfoLimiter = ""
if 'wfo[]' in form:
    aWFO = form['wfo[]']
    aWFO.append('XXX')  # Hack to make next section work
    if "ALL" not in aWFO:
        wfoLimiter = " and wfo in %s " % (str(tuple(aWFO)), )

sTS = datetime.datetime(year1, month1, day1, hour1, minute1)
eTS = datetime.datetime(year2, month2, day2, hour2, minute2)

os.chdir('/tmp')
fn = "lsr_%s_%s" % (sTS.strftime("%Y%m%d%H%M"), eTS.strftime("%Y%m%d%H%M"))
for suffix in ['shp', 'shx', 'dbf', 'csv']:
    if os.path.isfile("%s.%s" % (fn, suffix)):
        os.remove("%s.%s" % (fn, suffix))

csv = open("%s.csv" % (fn,), 'w')
csv.write(("VALID,VALID2,LAT,LON,MAG,WFO,TYPECODE,TYPETEXT,CITY,COUNTY,STATE,"
           "SOURCE,REMARK\n"))

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
               ) % (row[0], row[12], row[-3], row[-2], row[1], row[2], row[3],
                    row[4], row[5], row[6], row[7], row[8],
                    row[9].replace(",", "_") if row[9] is not None else ''))

csv.close()

shp = cStringIO.StringIO()
shx = cStringIO.StringIO()
dbf = cStringIO.StringIO()

w.save(shp=shp, shx=shx, dbf=dbf)

zio = cStringIO.StringIO()
zf = zipfile.ZipFile(zio, mode='w',
                     compression=zipfile.ZIP_DEFLATED)
zf.writestr(fn+'.prj',
            open(('/mesonet/www/apps/iemwebsite/data/gis/meta/4326.prj'
                  )).read())
zf.writestr(fn+".shp", shp.getvalue())
zf.writestr(fn+'.shx', shx.getvalue())
zf.writestr(fn+'.dbf', dbf.getvalue())
zf.writestr(fn+'.csv', open(fn+'.csv', 'r').read())
zf.close()


if "justcsv" in form:
    sys.stdout.write("Content-type: application/octet-stream\n")
    sys.stdout.write(("Content-Disposition: attachment; filename=%s.csv\n\n"
                      ) % (fn,))
    sys.stdout.write(open(fn+".csv", 'r').read())

else:
    sys.stdout.write(("Content-Disposition: attachment; "
                      "filename=%s.zip\n\n") % (fn,))
    sys.stdout.write(zio.getvalue())

os.remove(fn+".csv")
