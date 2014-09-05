#!/usr/bin/env python
#
# Download interface for the data stored in coop database (alldata)
#
import psycopg2.extras
import cgi
import sys
import datetime
from pyiem.network import Table as NetworkTable
from pyiem.datatypes import temperature

def ssw( txt ):
    """ shortcut """
    sys.stdout.write( txt )

def get_database():
    """ Get database """
    return psycopg2.connect(database="coop", host="iemdb", user="nobody")

def get_cgi_dates(form):
    """ Figure out which dates are requested """
    y1 = int(form.getfirst('year1'))
    m1 = int(form.getfirst('month1'))
    d1 = int(form.getfirst('day1'))
    y2 = int(form.getfirst('year2'))
    m2 = int(form.getfirst('month2'))
    d2 = int(form.getfirst('day2'))

    return [datetime.datetime(y1, m1, d1), datetime.datetime(y2, m2, d2)]

def get_cgi_stations(form):
    """ Figure out which stations the user wants, return a list of them """
    reqlist = form.getlist("station[]")
    if "_ALL" in reqlist:
        network = form.getfirst("network")
        nt = NetworkTable(network)
        return nt.sts.keys()
        
    return reqlist

def do_apsim( ctx ):
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
                          +"permitted for one station at a time."))
        return
    
    dbconn = get_database()
    cursor = dbconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    station = ctx['stations'][0]
    table = get_tablename(ctx['stations'])
    network = "%sCLIMATE" % (station[:2],)
    nt = NetworkTable(network)
    
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
    
    ssw("""year          day           radn          maxt          mint          rain
()            ()            (MJ/m^2)      (oC)          (oC)          (mm)\n""")

    thisyear = datetime.datetime.now().year
    extra = {}
    if ctx['scenario'] == 'yes':
        sts = datetime.datetime(int(ctx['scenario_year']), 1, 1)
        ets = datetime.datetime(int(ctx['scenario_year']), 12, 31)
        cursor.execute("""
            SELECT day, high, low, precip,
            coalesce(narr_srad, merra_srad, hrrr_srad) as srad
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
    
    cursor.execute("""
        SELECT day, high, low, precip, 
        coalesce(narr_srad, merra_srad, hrrr_srad) as srad
        from """+table+""" 
        WHERE station = %s and 
        day >= %s and day <= %s ORDER by day ASC
        """, (station, ctx['sts'], ctx['ets']) )
    for row in cursor:
        srad = -99 if row['srad'] is None else row['srad']
        ssw(" %s         %.0f        %.4f         %.4f      %.4f     %.2f\n" % (
            row["day"].year, int(row["day"].strftime("%j")), srad, 
            temperature(row["high"], 'F').value('C'), 
            temperature(row["low"], 'F').value('C'), 
            row["precip"] * 25.4 ))
    

    if len(extra) > 0:
        dec31 = datetime.date(thisyear, 12, 31)
        now = row['day']
        while now <= dec31:
            row = extra[now]
            ssw(" %s         %.0f        %.4f         %.4f      %.4f     %.2f\n" % ( 
                now.year, int(now.strftime("%j")), srad, 
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

    dbconn = get_database()
    cursor = dbconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    sts = datetime.date(ctx['sts'].year, 1, 1)
    ets = datetime.date(ctx['ets'].year, 12, 31)

    scenario_year= 2030    
    asts = datetime.date(2030, 1, 1)
    if ctx['scenario'] == 'yes':
        # Tricky!
        scenario_year = ctx['scenario_year']
        today = datetime.date.today()
        asts = datetime.date(scenario_year, today.month, today.day)
        pass
    
    table = get_tablename(ctx['stations'])
    thisyear = datetime.datetime.now().year
    cursor.execute("""
    WITH scenario as (
        SELECT """+str(thisyear)+"""::int as year, month, high, low, precip
        from """+table+"""
        WHERE station = %s and day > %s and year = %s and sday != '0229'
    ), obs as (
      select year, month, high, low, precip from """+table+"""
      WHERE station = %s and day >= %s and day <= %s
    ), data as (
      SELECT * from obs UNION select * from scenario
    )
    
    SELECT year, month, avg(high) as tmax, avg(low) as tmin,
    sum(precip) as prec from data GROUP by year, month
    """, (ctx['stations'][0], asts, scenario_year, ctx['stations'][0], sts, ets))
    data = {}
    for row in cursor:
        if not data.has_key(row['year']):
            data[ row['year'] ] = {}
        
        data[ row['year'] ][ row['month'] ] = {
             'prec' :  row['prec'] * 24.5,
             'tmin' : temperature(float(row['tmin']), 'F').value('C'),
             'tmax' : temperature(float(row['tmax']), 'F').value('C'),                                               
            }
    
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
    
def do_daycent( ctx ):
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
    
    cursor.execute("""
        SELECT day, high, low, precip
        from """+table+""" WHERE station = %s 
        and day >= %s and day <= %s ORDER by day ASC
        """, (ctx['stations'][0], ctx['sts'], ctx['ets']) )
    ssw("Daily Weather Data File (use extra weather drivers = 0):\n\n")
    for row in cursor:
        ssw("%s %s %s %s %.2f %.2f %.2f\n" % (row["day"].day, 
                                                  row["day"].month, 
                row["day"].year, int(row["day"].strftime("%j")), f2c(row["high"]), 
                f2c(row["low"]), row["precip"] * 25.4) )
    if len(extra) > 0:
        dec31 = datetime.date(thisyear, 12, 31)
        now = row['day']
        while now <= dec31:
            row = extra[now]
            ssw("%s %s %s %s %.2f %.2f %.2f\n" % (now.day, 
                now.month,  now.year, int(now.strftime("%j")), 
                f2c(row["high"]), f2c(row["low"]), row["precip"] * 25.4) )
            now += datetime.timedelta(days=1)

def get_tablename(stations):
    """ Figure out the table that has the data for these stations """
    return "alldata_%s" % (stations[0][:2],)

def f2c(val):
    """ Convert temperature in F to C """
    return temperature(val, 'F').value('C')

if __name__ == '__main__':
    # See how we are called
    form = cgi.FieldStorage()
    ctx = {}
    ctx['stations'] = get_cgi_stations(form)
    ctx['sts'], ctx['ets'] = get_cgi_dates(form)
    ctx['myvars'] = form.getlist("vars[]")
    ctx['what'] = form.getfirst('what', 'view')
    ctx['delim'] = form.getfirst('delim', 'comma')
    ctx['inclatlon'] = form.getfirst('gis', 'no')
    ctx['scenario'] = form.getfirst('scenario', 'no')
    ctx['scenario_year'] = int(form.getfirst('scenario_year', 0))
    
    if ctx['what'] == 'dl':
        ssw("Content-type: application/octet-stream\n")
        ssw(("Content-Disposition: attachment; "
                          +"filename=changeme.txt\n\n"))        
    else:
        ssw("Content-type: text/plain\n\n")
        
    
    # OK, now we fret
    if "daycent" in ctx['myvars']:
        do_daycent( ctx )
    elif "century" in ctx['myvars']:
        do_century( ctx )
    elif "apsim" in ctx['myvars']:
        do_apsim( ctx )
    
