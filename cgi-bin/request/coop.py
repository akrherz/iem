#!/usr/bin/env python
"""
 Download interface for the data stored in coop database (alldata)

 This is called from /request/coop/fe.phtml

"""

import psycopg2.extras
import cgi
import os
import sys
import datetime
import zipfile
import pandas as pd
from pyiem.network import Table as NetworkTable
from pyiem.datatypes import temperature, distance
import StringIO
import unittest


def get_scenario_period(ctx):
    """ Compute the inclusive start and end dates to fetch scenario data for
    Arguments:
        ctx dictionary context this app was called with
    """
    sts = datetime.date(ctx['scenario_year'], ctx['sts'].month, ctx['sts'].day)
    ets = datetime.date(ctx['scenario_year'], 12, 31)
    return sts, ets


def ssw(txt):
    """ shortcut """
    sys.stdout.write(txt)


def get_database():
    """ Get database """
    return psycopg2.connect(database="coop", host="iemdb", user="nobody")


def sane_date(year, month, day):
    """ Attempt to account for usage of days outside of the bounds for
    a given month """
    # Calculate the last date of the given month
    nextmonth = datetime.date(year, month, 1) + datetime.timedelta(days=35)
    lastday = nextmonth.replace(day=1) - datetime.timedelta(days=1)
    return datetime.date(year, month, min(day, lastday.day))


def get_cgi_dates(form):
    """ Figure out which dates are requested via the form, we shall attempt
    to account for invalid dates provided! """
    y1 = int(form.getfirst('year1'))
    m1 = int(form.getfirst('month1'))
    d1 = int(form.getfirst('day1'))
    y2 = int(form.getfirst('year2'))
    m2 = int(form.getfirst('month2'))
    d2 = int(form.getfirst('day2'))

    ets = sane_date(y2, m2, d2)
    archive_end = datetime.date.today() - datetime.timedelta(days=1)
    if ets > archive_end:
        ets = archive_end

    return [sane_date(y1, m1, d1), ets]


def get_cgi_stations(form):
    """ Figure out which stations the user wants, return a list of them """
    reqlist = form.getlist("station[]")
    if len(reqlist) == 0:
        reqlist = form.getlist('stations')
    if len(reqlist) == 0:
        ssw("Content-type: text/plain\n\n")
        ssw("No stations or station[] specified, need at least one station!")
        sys.exit()
    if "_ALL" in reqlist:
        network = form.getfirst("network")
        nt = NetworkTable(network)
        return nt.sts.keys()

    return reqlist


def do_apsim(ctx):
    """
    [weather.met.weather]
    latitude = 42.1 (DECIMAL DEGREES)
    tav = 9.325084 (oC) ! annual average ambient temperature
    amp = 29.57153 (oC) ! annual amplitude in mean monthly temperature
    year          day           radn          maxt          mint          rain
    ()            ()            (MJ/m^2)      (oC)          (oC)          (mm)
     1986          1             7.38585       0.8938889    -7.295556      0
     """
    if len(ctx['stations']) > 1:
        ssw(("ERROR: APSIM output is only "
             "permitted for one station at a time."))
        return

    dbconn = get_database()
    cursor = dbconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = ctx['stations'][0]
    table = get_tablename(ctx['stations'])
    network = "%sCLIMATE" % (station[:2],)
    nt = NetworkTable(network)

    thisyear = datetime.datetime.now().year
    extra = {}
    if ctx['scenario'] == 'yes':
        sts = datetime.datetime(int(ctx['scenario_year']), 1, 1)
        ets = datetime.datetime(int(ctx['scenario_year']), 12, 31)
        cursor.execute("""
            SELECT day, high, low, precip, 1 as doy,
            coalesce(narr_srad, merra_srad, hrrr_srad) as srad
            from """ + table + """ WHERE station = %s
            and day >= %s and day <= %s
            """, (ctx['stations'][0], sts, ets))
        for row in cursor:
            ts = row[0].replace(year=thisyear)
            extra[ts] = row
            extra[ts]['doy'] = int(ts.strftime("%j"))
        febtest = datetime.date(thisyear, 3, 1) - datetime.timedelta(days=1)
        if febtest not in extra:
            feb28 = datetime.date(thisyear, 2, 28)
            extra[febtest] = extra[feb28]

    ssw("! Iowa Environmental Mesonet -- NWS Cooperative Data\n")
    ssw("! Created: %s UTC\n" % (
                datetime.datetime.utcnow().strftime("%d %b %Y %H:%M:%S"),))
    ssw("! Contact: daryl herzmann akrherz@iastate.edu 515-294-5978\n")
    ssw("! Station: %s %s\n" % (station, nt.sts[station]['name']))
    ssw("! Data Period: %s - %s\n" % (ctx['sts'], 
                                      ctx['ets']))
    if ctx['scenario'] == 'yes':
        ssw("! !SCENARIO DATA! inserted after: %s replicating year: %s\n" % (
                            ctx['ets'], ctx['scenario_year']))

    ssw("[weather.met.weather]\n")
    ssw("latitude = %.1f (DECIMAL DEGREES)\n" % ( nt.sts[ station ]["lat"]) )

    # Compute average temperature!
    cursor.execute("""
        SELECT avg((high+low)/2) as avgt from climate51 WHERE station = %s 
        """, (station,))
    row = cursor.fetchone()
    ssw("tav = %.3f (oC) ! annual average ambient temperature\n" % (
            temperature(row['avgt'], 'F').value('C'),))

    # Compute the annual amplitude in temperature
    cursor.execute("""
        select max(avg) as h, min(avg) as l from
            (SELECT extract(month from valid) as month, avg((high+low)/2.)
             from climate51 
             WHERE station = %s GROUP by month) as foo
             """, (station,) )
    row = cursor.fetchone()
    ssw("amp = %.3f (oC) ! annual amplitude in mean monthly temperature\n" % (
        (temperature(row['h'], 'F').value('C') - 
        temperature(row['l'], 'F').value('C')), ))

    ssw("""year        day       radn       maxt       mint      rain
  ()         ()   (MJ/m^2)       (oC)       (oC)       (mm)\n""")

    if ctx.get('hayhoe_model') is not None:
        cursor.execute("""
            SELECT day, high, low, precip,
            extract(doy from day) as doy,
            0 as srad
            from hayhoe_daily WHERE station = %s
            and day >= %s and scenario = %s and model = %s
            ORDER by day ASC
        """, (ctx['stations'][0], ctx['sts'],
              ctx['hayhoe_scenario'], ctx['hayhoe_model']))
    else:
        cursor.execute("""
            SELECT day, high, low, precip,
            extract(doy from day) as doy,
            coalesce(narr_srad, merra_srad, hrrr_srad) as srad
            from """ + table + """
            WHERE station = %s and
            day >= %s and day <= %s ORDER by day ASC
            """, (station, ctx['sts'], ctx['ets']))
    for row in cursor:
        srad = -99 if row['srad'] is None else row['srad']
        ssw("%4s %10.0f %10.3f %10.1f %10.1f %10.2f\n" % (
            row["day"].year, int(row["doy"]), srad, 
            temperature(row["high"], 'F').value('C'), 
            temperature(row["low"], 'F').value('C'), 
            row["precip"] * 25.4 ))

    if len(extra) > 0:
        dec31 = datetime.date(thisyear, 12, 31)
        now = row['day']
        while now <= dec31:
            row = extra[now]
            srad = -99 if row['srad'] is None else row['srad']
            ssw("%4s %10.0f %10.3f %10.1f %10.1f %10.2f\n" % ( 
                now.year, int(row['doy']), srad, 
                temperature(row["high"], 'F').value('C'), 
                temperature(row["low"], 'F').value('C'), 
                row["precip"] * 25.4 ) )
            now += datetime.timedelta(days=1)


def do_century( ctx ):
    """ Materialize the data in Century Format 
    * Century format  (precip cm, avg high C, avg low C)
    prec  1980   2.60   6.40   0.90   1.00   0.70   0.00  
    tmin  1980  14.66  12.10   7.33  -0.89  -5.45  -7.29
    tmax  1980  33.24  30.50  27.00  18.37  11.35   9.90  
    prec  1981  12.00   7.20   0.60   4.90   1.10   0.30 
    tmin  1981  14.32  12.48   8.17   0.92  -3.25  -8.90 
    tmax  1981  30.84  28.71  27.02  16.84  12.88   6.82 
    """
    if len(ctx['stations']) > 1:
        ssw(("ERROR: Century output is only "
                          +"permitted for one station at a time."))
        return

    station = ctx['stations'][0]
    network = "%sCLIMATE" % (station[:2],)
    nt = NetworkTable(network)
    
    dbconn = get_database()
    cursor = dbconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Automatically set dates to start and end of year to make output clean
    sts = datetime.date(ctx['sts'].year, 1, 1)
    ets = datetime.date(ctx['ets'].year, 12, 31)
    if ets >= datetime.date.today():
        ets = datetime.date.today() - datetime.timedelta(days=1)
    
    table = get_tablename(ctx['stations'])
    thisyear = datetime.datetime.now().year
    cursor.execute("""
    WITH scenario as (
        SELECT """+str(thisyear)+"""::int as year, month, high, low, precip
        from """+table+"""
        WHERE station = %s and day > %s and day <= %s and sday != '0229'
    ), obs as (
      select year, month, high, low, precip from """+table+"""
      WHERE station = %s and day >= %s and day <= %s
    ), data as (
      SELECT * from obs UNION select * from scenario
    )
    
    SELECT year, month, avg(high) as tmax, avg(low) as tmin,
    sum(precip) as prec from data GROUP by year, month
    """, (station, ctx['scenario_sts'], ctx['scenario_ets'], 
          station, sts, ets))
    data = {}
    for row in cursor:
        if not data.has_key(row['year']):
            data[ row['year'] ] = {}
            for mo in range(1, 13):
                data[ row['year'] ][mo] = {'prec': -99, 'tmin': -99,
                                           'tmax': -99}
        
        data[ row['year'] ][ row['month'] ] = {
             'prec' :  distance(row['prec'], 'IN').value('MM'),
             'tmin' : temperature(float(row['tmin']), 'F').value('C'),
             'tmax' : temperature(float(row['tmax']), 'F').value('C'),
            }

    ssw("# Iowa Environmental Mesonet -- NWS Cooperative Data\n")
    ssw("# Created: %s UTC\n" % (
                datetime.datetime.utcnow().strftime("%d %b %Y %H:%M:%S"),))
    ssw("# Contact: daryl herzmann akrherz@iastate.edu 515-294-5978\n")
    ssw("# Station: %s %s\n" % (station, nt.sts[station]['name']))
    ssw("# Data Period: %s - %s\n" % (sts, ets))
    if ctx['scenario'] == 'yes':
        ssw("# !SCENARIO DATA! inserted after: %s replicating year: %s\n" % (
                            ctx['ets'], ctx['scenario_year']))
    idxs = ["prec", "tmin", "tmax"]
    for year in range(sts.year, ets.year+1):
        for idx in idxs:
            ssw(("%s  %s%7.2f%7.2f%7.2f%7.2f%7.2f%7.2f%7.2f"
                    +"%7.2f%7.2f%7.2f%7.2f%7.2f\n") % (idx, year,
                    data[year][1][idx], data[year][2][idx],
                    data[year][3][idx], data[year][4][idx],
                    data[year][5][idx], data[year][6][idx],
                    data[year][7][idx], data[year][8][idx],
                    data[year][9][idx], data[year][10][idx],
                    data[year][11][idx], data[year][12][idx]
                    ))

def do_daycent(ctx):
    """ Materialize data for daycent

    Daily Weather Data File (use extra weather drivers = 0):
    > 1 1 1990 1 7.040 -10.300 0.000
 
    NOTES:
    Column 1 - Day of month, 1-31
    Column 2 - Month of year, 1-12
    Column 3 - Year
    Column 4 - Day of the year, 1-366
    Column 5 - Maximum temperature for day, degrees C
    Column 6 - Minimum temperature for day, degrees C
    Column 7 - Precipitation for day, centimeters    
    """
    if len(ctx['stations']) > 1:
        ssw(("ERROR: Daycent output is only "
                          +"permitted for one station at a time."))
        return

    dbconn = get_database()
    cursor = dbconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    table = get_tablename(ctx['stations'])
    
    extra = {}
    thisyear = datetime.datetime.now().year
    if ctx['scenario'] == 'yes':
        sts = datetime.datetime(int(ctx['scenario_year']), 1, 1)
        ets = datetime.datetime(int(ctx['scenario_year']), 12, 31)
        cursor.execute("""
            SELECT day, high, low, precip
            from """+table+""" WHERE station = %s 
            and day >= %s and day <= %s
            """, (ctx['stations'][0], sts, ets))
        for row in cursor:
            ts = row[0].replace(year=thisyear)
            extra[ ts ] = row
        febtest = datetime.date(thisyear, 3, 1 ) - datetime.timedelta(days=1)
        if not extra.has_key(febtest):
            feb28 = datetime.date(thisyear, 2, 28)
            extra[febtest] = extra[feb28]
    if ctx.get('hayhoe_model') is not None:
        cursor.execute("""
            SELECT day, high, low, precip,
            extract(doy from day) as doy
            from hayhoe_daily WHERE station = %s 
            and day >= %s and scenario = %s and model = %s
            ORDER by day ASC
        """, (ctx['stations'][0], ctx['sts'],
              ctx['hayhoe_scenario'], ctx['hayhoe_model']) )        
    else:
        cursor.execute("""
            SELECT day, high, low, precip,
            extract(doy from day) as doy
            from """+table+""" WHERE station = %s 
            and day >= %s and day <= %s ORDER by day ASC
        """, (ctx['stations'][0], ctx['sts'], ctx['ets']) )
    ssw("Daily Weather Data File (use extra weather drivers = 0):\n\n")
    for row in cursor:
        ssw("%s %s %s %s %.2f %.2f %.2f\n" % (row["day"].day, 
            row["day"].month, row["day"].year, int(row["doy"]),
            f2c(row["high"]), f2c(row["low"]),
            distance(row["precip"], 'IN').value('CM')))
    if len(extra) > 0:
        dec31 = datetime.date(thisyear, 12, 31)
        now = row['day']
        while now <= dec31:
            row = extra[now]
            ssw("%s %s %s %s %.2f %.2f %.2f\n" % (now.day, 
                now.month,  now.year, int(now.strftime("%j")), 
                f2c(row["high"]), f2c(row["low"]),
                distance(row["precip"], 'IN').value('CM')))
            now += datetime.timedelta(days=1)


def get_tablename(stations):
    """ Figure out the table that has the data for these stations """
    states = []
    for sid in stations:
        if sid[:2] not in states:
            states.append( sid[:2])
    if len(states) == 1:
        return "alldata_%s" % (states[0],)
    return "alldata"


def get_stationtable(stations):
    """ Figure out our station table! """
    states = []
    networks = []
    for sid in stations:
        if sid[:2] not in states:
            states.append(sid[:2])
            networks.append("%sCLIMATE" % (sid[:2],))
    return NetworkTable(networks)


def f2c(val):
    """ Convert temperature in F to C """
    return temperature(val, 'F').value('C')


def do_simple(ctx):
    """ Generate Simple output  """

    dbconn = get_database()
    cursor = dbconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    table = get_tablename(ctx['stations'])

    nt = get_stationtable(ctx['stations'])
    thisyear = datetime.datetime.now().year
    if len(ctx['stations']) == 1:
        ctx['stations'].append('X')

    sql = """
    WITH scenario as (
        SELECT station, high, low, precip, snow, snowd, narr_srad,
        merra_srad, merra_srad_cs, hrrr_srad,
 to_char(('"""+str(thisyear)+"""-'||month||'-'||extract(day from day))::date,
        'YYYY/mm/dd') as day,
        extract(doy from day) as julianday,
        gddxx(50, 86, high, low) as gdd_50_86,
        gddxx(40, 86, high, low) as gdd_40_86,
        round((5.0/9.0 * (high - 32.0))::numeric,1) as highc,
        round((5.0/9.0 * (low - 32.0))::numeric,1) as lowc,
        round((precip * 25.4)::numeric,1) as precipmm
        from """ + table + """ WHERE
        station IN """ + str(tuple(ctx['stations'])) + """ and
        day >= %s and day <= %s
    ), obs as (
        SELECT station, high, low, precip, snow, snowd, narr_srad,
        merra_srad, merra_srad_cs, hrrr_srad,
        to_char(day, 'YYYY/mm/dd') as day,
        extract(doy from day) as julianday,
        gddxx(50, 86, high, low) as gdd_50_86,
        gddxx(40, 86, high, low) as gdd_40_86,
        round((5.0/9.0 * (high - 32.0))::numeric,1) as highc,
        round((5.0/9.0 * (low - 32.0))::numeric,1) as lowc,
        round((precip * 25.4)::numeric,1) as precipmm
        from """+table+""" WHERE
        station IN """ + str(tuple(ctx['stations'])) + """ and
        day >= %s and day <= %s
    ), total as (
        SELECT * from obs UNION SELECT * from scenario
    )

    SELECT * from total ORDER by day ASC"""
    args = (ctx['scenario_sts'], ctx['scenario_ets'], ctx['sts'], ctx['ets'])

    cols = ['station', 'station_name', 'day', 'julianday']
    if ctx['inclatlon'] == 'yes':
        cols.insert(2, 'lat')
        cols.insert(3, 'lon')

    cols = cols + ctx['myvars']

    if ctx['what'] == 'excel':
        # Do the excel logic
        df = pd.read_sql(sql, dbconn, params=args)

        def _gs(x, y):
            return nt.sts[x][y]

        df['station_name'] = [_gs(x, 'name') for x in df['station']]
        if 'lat' in cols:
            df['lat'] = [_gs(x, 'lat') for x in df['station']]
            df['lon'] = [_gs(x, 'lon') for x in df['station']]
        ssw("Content-type: application/vnd.ms-excel\n")
        ssw("Content-Disposition: attachment;Filename=nwscoop.xls\n\n")
        df.to_excel('/tmp/ss.xls', columns=cols, index=False)
        ssw(open('/tmp/ss.xls', 'rb').read())
        os.unlink('/tmp/ss.xls')
        return

    cursor.execute(sql, args)

    ssw("# Iowa Environmental Mesonet -- NWS Cooperative Data\n")
    ssw("# Created: %s UTC\n" % (
                datetime.datetime.utcnow().strftime("%d %b %Y %H:%M:%S"),))
    ssw("# Contact: daryl herzmann akrherz@iastate.edu 515-294-5978\n")
    ssw("# Data Period: %s - %s\n" % (ctx['sts'], ctx['ets']))
    if ctx['scenario'] == 'yes':
        ssw("# !SCENARIO DATA! inserted after: %s replicating year: %s\n" % (
                            ctx['ets'], ctx['scenario_year']))


    p = {'comma': ',', 'tab': '\t', 'space': ' '}
    d = p[ ctx['delim'] ]
    ssw( d.join( cols ) +"\r\n")

    for row in cursor:
        sid = row["station"]
        dc = row.copy()
        dc['station_name'] = nt.sts[sid]['name']
        dc['lat'] = "%.4f" % (nt.sts[sid]['lat'],)
        dc['lon'] = "%.4f" % (nt.sts[sid]['lon'],)
        dc['julianday'] = "%.0f" % (dc['julianday'],)
        res = []
        for n in cols:
            res.append( str(dc[n]) )
        ssw( (d.join(res)).replace("None", "M") +"\r\n")


def do_salus( ctx ):
    """ Generate SALUS
    StationID, Year, DOY, SRAD, Tmax, Tmin, Rain, DewP, Wind, Par, dbnum
    CTRL, 1981, 1, 5.62203, 2.79032, -3.53361, 5.43766, NaN, NaN, NaN, 2
    CTRL, 1981, 2, 3.1898, 1.59032, -6.83361, 1.38607, NaN, NaN, NaN, 3 
    """
    if len(ctx['stations']) > 1:
        ssw(("ERROR: SALUS output is only "
                          +"permitted for one station at a time."))
        return

    dbconn = get_database()
    cursor = dbconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    scenario_year = 2030    
    asts = datetime.date(2030, 1, 1)
    if ctx['scenario'] == 'yes':
        # Tricky!
        scenario_year = ctx['scenario_year']
        today = datetime.date.today()
        asts = datetime.date(scenario_year, today.month, today.day)
    
    table = get_tablename(ctx['stations'])
    station = ctx['stations'][0]
    thisyear = datetime.datetime.now().year
    cursor.execute("""
    WITH scenario as (
        SELECT 
    ('"""+str(thisyear)+"""-'||month||'-'||extract(day from day))::date as day,
        high, low, precip, station,
        coalesce(narr_srad, merra_srad, hrrr_srad) as srad 
        from """+table+""" WHERE station = %s and 
        day >= %s and year = %s
    ), obs as (    
        SELECT day, 
        high, low, precip,  station, 
        coalesce(narr_srad, merra_srad, hrrr_srad) as srad
        from """+table+""" WHERE station = %s and 
        day >= %s and day <= %s ORDER by day ASC
    ), total as (
        SELECT *, extract(doy from day) as doy from obs 
        UNION SELECT * from scenario
    )
    
    SELECT * from total ORDER by day ASC
    """, (station, asts, scenario_year, station, ctx['sts'], ctx['ets']) )
    ssw(("StationID, Year, DOY, SRAD, Tmax, Tmin, Rain, DewP, "
         +"Wind, Par, dbnum\n"))
    for i, row in enumerate(cursor):
        srad = -99 if row['srad'] is None else row['srad']
        ssw("%s, %s, %s, %.4f, %.2f, %.2f, %.2f, , , , %s\n" % ( 
                station[:4], row["day"].year,
                int(row["doy"]), srad,  
                temperature(row["high"], 'F').value('C'), 
                temperature(row["low"], 'F').value('C'), 
                row["precip"] * 25.4, i + 2))

def do_dndc( ctx ):
    """ Process DNDC 
    * One file per year! named StationName / StationName_YYYY.txt
    * julian day, tmax C , tmin C, precip cm seperated by space
    """
    dbconn = get_database()
    cursor = dbconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    table = get_tablename(ctx['stations'])
    
    nt = get_stationtable(ctx['stations'])
    
    if len(ctx['stations']) == 1:
        ctx['stations'].append('X')
        
    scenario_year = 2030    
    asts = datetime.date(2030, 1, 1)
    if ctx['scenario'] == 'yes':
        # Tricky!
        scenario_year = ctx['scenario_year']
        today = datetime.date.today()
        asts = datetime.date(scenario_year, today.month, today.day)
        
    thisyear = datetime.datetime.now().year
    cursor.execute("""
        WITH scenario as (
            SELECT 
    ('"""+str(thisyear)+"""-'||month||'-'||extract(day from day))::date as day,
            high, low, precip, station from """+table+"""
            WHERE station IN """+ str(tuple(ctx['stations'])) +""" and 
            day >= %s and year = %s),
        obs as (
            SELECT day, high, low, precip, station from """+table+"""
            WHERE station IN """+ str(tuple(ctx['stations'])) +""" and 
            day >= %s and day <= %s),
        total as (
            SELECT *, extract(doy from day) as doy from obs UNION 
            SELECT *, extract(doy from day) as doy from scenario
        )
        
        SELECT * from total ORDER by day ASC 
    """, (asts, scenario_year, ctx['sts'], ctx['ets']))
    zipfiles = {}
    for row in cursor:
        station = row['station']
        sname = nt.sts[station]['name'].replace(" ", "_")
        fn = "%s/%s_%s.txt" % (sname, sname, row['day'].year)
        if not zipfiles.has_key(fn):
            zipfiles[fn] = ""
        zipfiles[fn] += "%s %.2f %.2f %.2f\n" % ( 
                        int(row["doy"]), 
                        temperature(row["high"], 'F').value('C'), 
                        temperature(row["low"], 'F').value('C'), 
                        row["precip"] * 2.54 )

    sio = StringIO.StringIO()
    z = zipfile.ZipFile(sio, 'a')
    for fn in zipfiles.keys():
        z.writestr(fn, zipfiles[fn])
    z.close()
    ssw("Content-type: application/octet-stream\n")
    ssw("Content-Disposition: attachment; filename=dndc.zip\n\n")
    sio.seek(0)
    ssw(sio.read())


def main():
    """ go main go """
    form = cgi.FieldStorage()
    ctx = {}
    ctx['stations'] = get_cgi_stations(form)
    ctx['sts'], ctx['ets'] = get_cgi_dates(form)
    ctx['myvars'] = form.getlist("vars[]")
    ctx['what'] = form.getfirst('what', 'view')
    ctx['delim'] = form.getfirst('delim', 'comma')
    ctx['inclatlon'] = form.getfirst('gis', 'no')
    ctx['scenario'] = form.getfirst('scenario', 'no')
    ctx['hayhoe_scenario'] = form.getfirst('hayhoe_scenario')
    ctx['hayhoe_model'] = form.getfirst('hayhoe_model')
    if ctx['scenario'] == 'yes':
        ctx['scenario_year'] = int(form.getfirst('scenario_year', 2099))
    else:
        ctx['scenario_year'] = 2099
    ctx['scenario_sts'], ctx['scenario_ets'] = get_scenario_period(ctx)

    if "apsim" in ctx['myvars']:
        ssw("Content-type: text/plain\n\n")
    elif "dndc" not in ctx['myvars'] and ctx['what'] != 'excel':
        if ctx['what'] == 'download':
            ssw("Content-type: application/octet-stream\n")
            ssw(("Content-Disposition: attachment; "
                 "filename=changeme.txt\n\n"))
        else:
            ssw("Content-type: text/plain\n\n")

    # OK, now we fret
    if "daycent" in ctx['myvars']:
        do_daycent(ctx)
    elif "century" in ctx['myvars']:
        do_century(ctx)
    elif "apsim" in ctx['myvars']:
        do_apsim(ctx)
    elif "dndc" in ctx['myvars']:
        do_dndc(ctx)
    elif "salus" in ctx['myvars']:
        do_salus(ctx)
    else:
        do_simple(ctx)

if __name__ == '__main__':
    main()


class tests(unittest.TestCase):

    def test_sane_date(self):
        """ Test our sane_date() method"""
        self.assertEquals(sane_date(2000, 9, 31), datetime.date(2000, 9, 30))
        self.assertEquals(sane_date(2000, 2, 31), datetime.date(2000, 2, 29))
        self.assertEquals(sane_date(2000, 1, 15), datetime.date(2000, 1, 15))
