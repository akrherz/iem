#!/usr/bin/env python
'''
 Generate some QC for a station's worth of data?  This could get expensive
'''
#stdlib
import cgi
import sys
import datetime
# thirdparty
import psycopg2

IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
cursor = IEM.cursor()

COLS = []

def add_asos(station, date, data):
    ''' Include in ASOS nearby '''
    cursor.execute("""
    SELECT station, valid, phour from hourly 
    WHERE station in (select s1.id from stations s1, stations s2 WHERE 
                        s2.id = %s and s2.network = 'IA_COOP' and 
                        s1.network in ('IA_ASOS', 'AWOS') 
                        ORDER by ST_distance(s1.geom, s2.geom) ASC LIMIT 5)
    and valid BETWEEN %s - '24 hours'::interval and %s + '24 hours'::interval
    and phour > 0
    """, (station, date, date))
    for row in cursor:
        valid = row[1]
        if not data.has_key(valid):
            data[valid] = {}
        data[valid][row[0]] = row[2]
        if row[0] not in COLS:
            COLS.append( row[0] )

def printer(data, station, coopvalid):
    ''' Print out the data '''
    sts = coopvalid - datetime.timedelta(hours=24)
    ets = coopvalid + datetime.timedelta(hours=24)
    
    now = sts
    s = "                "
    for col in COLS:
        s += "%6s" % (col,)
    s += "\n"
    while now <= ets:
        s += "%s" % (now.strftime("%Y-%m-%d %H:%M"),)
        for col in COLS:
            val = data.get(now, {}).get(col, None)
            if val is None:
                s += "      "
            else:
                s += "%6.2f" % (val,)
        s += "\n"
        now += datetime.timedelta(hours=1)
    return s

def do(station, date):
    ''' Run for this date! '''
    data = {}
    cursor.execute("""
    SELECT pday, coop_valid 
    from summary s JOIN stations t on (t.iemid = s.iemid) WHERE
    network = 'IA_COOP' and t.id = %s and day = %s
    """, (station, date))
    if cursor.rowcount != 1:
        sys.stdout.write("ERROR! Could not found data for date!")
        return
    row = cursor.fetchone()
    if row[1] is None:
        sys.stdout.write("ERROR! COOP ob time is null")
        return
    data[ row[1] ] = {station: row[0]}
    
    add_asos(station, date, data)
    
    sys.stdout.write("<pre>\n")
    sys.stdout.write( printer(data, station, row[1]) )
    sys.stdout.write("</pre>\n")

if __name__ == '__main__':
    ''' see how we are called '''
    sys.stdout.write("Content-type: text/html\n\n")

    form = cgi.FieldStorage()
    station = form.getfirst('station', 'AMSI4')
    COLS.append( station )
    date = form.getfirst('date', None)
    if form.getfirst('date') is None:
        date = datetime.date.today()
    else:
        date = datetime.datetime.strptime(form.getfirst('date'), '%Y-%m-%d').date()
        
    do(station, date)