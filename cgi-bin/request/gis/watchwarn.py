#!/usr/bin/env python
"""Generate a shapefile of warnings based on the CGI request"""

import zipfile
import os
import shutil
import cgi
import pytz
import sys
import datetime
import psycopg2
from geopandas import GeoDataFrame

now = datetime.datetime.now()
has_error = False
error_message = 'Unknown error occurred'


def get_time_extent(form):
    """ Figure out the time extent of this request"""
    if 'year' in form:
        year1 = form.getfirst('year')
        year2 = form.getfirst('year')
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
    sts = sts.replace(tzinfo=pytz.timezone('UTC'))
    ets = datetime.datetime(int(year2), int(month2), int(day2),
                            int(hour2), int(minute2))
    ets = ets.replace(tzinfo=pytz.timezone('UTC'))
    return sts, ets


def parse_state_location_group(pg_connection, state_abbreviations):
    wfoLimiter = ''
    wfo_list = pull_wfos_in_states(pg_connection.cursor(), state_abbreviations)
    sys.stdout.write("Content-type: text/plain\n\n")
    if len(wfo_list) > 0:
        wfoLimiter = " and w.wfo in %s " % (str(tuple(wfo_list)),)

    return wfoLimiter


def parse_wfo_location_group():
    wfoLimiter = ''
    if 'wfo[]' in form:
        aWFO = form.getlist('wfo[]')
        aWFO.append('XXX')  # Hack to make next section work
        if 'ALL' not in aWFO:
            wfoLimiter = " and w.wfo in %s " % (str(tuple(aWFO)),)

    if 'wfos[]' in form:
        aWFO = form.getlist('wfos[]')
        aWFO.append('XXX')  # Hack to make next section work
        if 'ALL' not in aWFO:
            wfoLimiter = " and w.wfo in %s " % (str(tuple(aWFO)),)
    return wfoLimiter


def pull_wfos_in_states(pg_cursor, state_abbreviations):
    wfo_list = []

    try:
        pg_cursor.execute("""
            SELECT distinct wfo FROM stations WHERE state IN %s""" % (str(tuple(state_abbreviations)), ))

        if pg_cursor.rowcount > 0:
            rows = pg_cursor.fetchall()
            for row in rows:
                if row[0] is not None:
                    wfo_list.append(row[0])
    except Exception as e:
        msg = "Unexpected error: %s" % sys.exc_info()[0]
        sys.stdout.write(msg)
    return wfo_list

form = cgi.FieldStorage()
sts, ets = get_time_extent(form)
pgconn = psycopg2.connect(database='mesosite', host='iemdb', user='nobody')
mcursor = pgconn.cursor()

if 'location_group' in form:
    location_group = form.getfirst('location_group')
    if 'states' == location_group:
        if 'states[]' in form:
            states = form.getlist('states[]')
            wfoLimiter = parse_state_location_group(pgconn, states)
        else:
            error_message = 'No state specified'
            has_error = True
    elif 'wfo' == location_group:
        wfoLimiter = parse_wfo_location_group()
    else:
        # Unknown location_group
        has_error = True
        error_message = 'Unknown location_group (%s)' % (location_group, )
else:
    error_message = 'No location_group specified'
    has_error = True

if has_error:
    sys.stdout.write("Content-type: text/plain\n\n")
    sys.stdout.write("ERROR: %s" % (error_message, ))
    sys.exit()

# Change to postgis db once we have the wfo list
pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
fp = "wwa_%s_%s" % (sts.strftime("%Y%m%d%H%M"), ets.strftime("%Y%m%d%H%M"))
timeopt = int(form.getfirst('timeopt', [1])[0])
if timeopt == 2:
    year3 = int(form.getfirst('year3'))
    month3 = int(form.getfirst('month3'))
    day3 = int(form.getfirst('day3'))
    hour3 = int(form.getfirst('hour3'))
    minute3 = int(form.getfirst('minute3'))
    sts = datetime.datetime(year3, month3, day3, hour3, minute3)
    sts = sts.replace(tzinfo=pytz.timezone("UTC"))
    fp = "wwa_%s" % (sts.strftime("%Y%m%d%H%M"), )

os.chdir("/tmp/")
for suffix in ['shp', 'shx', 'dbf', 'txt', 'zip']:
    if os.path.isfile("%s.%s" % (fp, suffix)):
        os.remove("%s.%s" % (fp, suffix))

limiter = ""
if 'limit0' in form:
    limiter += (
        " and phenomena IN ('TO','SV','FF','MA') and significance = 'W' ")

sbwlimiter = " WHERE gtype = 'P' " if 'limit1' in form else ""

table1 = "warnings"
table2 = "sbw"
if sts.year == ets.year:
    table1 = "warnings_%s" % (sts.year,)
    if sts.year > 2001:
        table2 = "sbw_%s" % (sts.year,)
    else:
        table2 = 'sbw_2014'

geomcol = "geom"
if form.getfirst('simple', 'no') == 'yes':
    geomcol = "simple_geom"

cols = """geo, wfo, utc_issue as issued, utc_expire as expired,
 utc_prodissue as init_iss, utc_init_expire as init_exp, phenomena as phenom,
 gtype, significance as sig, eventid as etn,  status, ugc as nws_ugc,
 area2d as area_km2"""

timelimit = "issue >= '%s' and issue < '%s'" % (sts, ets)
if timeopt == 2:
    timelimit = "issue <= '%s' and issue > '%s' and expire > '%s'" % (
        sts, sts + datetime.timedelta(days=-30), sts)

sql = """
WITH stormbased as (
 SELECT geom as geo, 'P'::text as gtype, significance, wfo, status, eventid,
 ''::text as ugc,
 phenomena,
 ST_area( ST_transform(w.geom,2163) ) / 1000000.0 as area2d,
 to_char(expire at time zone 'UTC', 'YYYYMMDDHH24MI') as utc_expire,
 to_char(issue at time zone 'UTC', 'YYYYMMDDHH24MI') as utc_issue,
 to_char(issue at time zone 'UTC', 'YYYYMMDDHH24MI') as utc_prodissue,
 to_char(init_expire at time zone 'UTC', 'YYYYMMDDHH24MI') as utc_init_expire
 from %s w WHERE status = 'NEW' and %s %s %s
),
countybased as (
 SELECT u.%s as geo, 'C'::text as gtype,
 significance,
 w.wfo, status, eventid, u.ugc, phenomena,
 ST_area( ST_transform(u.geom,2163) ) / 1000000.0 as area2d,
 to_char(expire at time zone 'UTC', 'YYYYMMDDHH24MI') as utc_expire,
 to_char(issue at time zone 'UTC', 'YYYYMMDDHH24MI') as utc_issue,
 to_char(product_issue at time zone 'UTC', 'YYYYMMDDHH24MI') as utc_prodissue,
 to_char(init_expire at time zone 'UTC', 'YYYYMMDDHH24MI') as utc_init_expire
 from %s w JOIN ugcs u on (u.gid = w.gid) WHERE
 %s %s %s
 )
 SELECT %s from stormbased UNION SELECT %s from countybased %s
""" % (table2, timelimit, wfoLimiter, limiter,
       geomcol, table1, timelimit, wfoLimiter, limiter,
       cols, cols, sbwlimiter)


df = GeoDataFrame.from_postgis(sql, pgconn, 'geo')
if len(df.index) == 0:
    sys.stdout.write("Content-type: text/plain\n\n")
    sys.stdout.write("ERROR: No results found for query, please try again")
    sys.exit()

# Capitolize columns please
df.columns = [s.upper() if s != 'geo' else s for s in df.columns.values]
df.to_file(fp+".shp")

shutil.copyfile("/mesonet/www/apps/iemwebsite/data/gis/meta/4326.prj",
                fp+".prj")

z = zipfile.ZipFile(fp+".zip", 'w', zipfile.ZIP_DEFLATED)
z.write(fp+".shp")
z.write(fp+".shx")
z.write(fp+".dbf")
z.write(fp+".prj")
z.close()

sys.stdout.write("Content-type: application/octet-stream\n")
sys.stdout.write(
    "Content-Disposition: attachment; filename=%s.zip\n\n" % (fp,))
sys.stdout.write(file(fp+".zip", 'r').read())

for suffix in ['zip', 'shp', 'shx', 'dbf', 'prj']:
    os.remove("%s.%s" % (fp, suffix))
