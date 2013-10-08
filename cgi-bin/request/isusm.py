#!/usr/bin/env python
''' 
 Download interface for ISU-SM data
'''
import cgi
import datetime
import psycopg2
import sys
sys.path.insert(0, '/home/akrherz/projects/pyIEM')
from pyiem.datatypes import temperature
ISUAG = psycopg2.connect(database='isuag', host='iemdb', user='nobody')
cursor = ISUAG.cursor()

def get_stations( form ):
    ''' Figure out which stations were requested '''
    stations = form.getlist('sts')
    if len(stations) == 0:
        stations.append('XXXXX')
    if len(stations) == 1:
        stations.append('XXXXX')
    return stations

def get_dates( form ):
    ''' Get the start and end dates requested '''
    year1 = form.getfirst('year1', 2013)
    month1 = form.getfirst('month1', 1)
    day1 = form.getfirst('day1', 1)
    year2 = form.getfirst('year2', 2013)
    month2 = form.getfirst('month2', 1)
    day2 = form.getfirst('day2', 1)

    sts = datetime.datetime( int(year1), int(month1), int(day1))
    ets = datetime.datetime( int(year2), int(month2), int(day2))
    
    return sts, ets

def get_delimiter( form ):
    ''' Figure out what is the requested delimiter '''
    d = form.getvalue('delim', 'comma')
    if d == 'comma':
        return ','
    return '\t'


def fetch_daily( form ):
    ''' Return a fetching of daily data '''
    sts, ets = get_dates( form )
    stations = get_stations( form )
    delim = get_delimiter( form )
    
    res = delim.join( ["station","valid","high"] ) + "\n"
    
    sql = """SELECT station, valid, tair_c_max from sm_daily 
    WHERE valid >= '%s 00:00' and valid < '%s 00:00' and station in %s
    ORDER by valid ASC
    """ % (sts.strftime("%Y-%m-%d"), ets.strftime("%Y-%m-%d"), 
           str(tuple(stations)))
    cursor.execute(sql)
    
    for row in cursor:
        if row[2] is None:
            tmpf = -99
        else:
            tmpf = temperature(row[2], 'C').value('F')
        valid = row[1]
        station = row[0]
        
        res += "%s%s%s%s%.1f\n" % (station, delim, 
                                   valid.strftime("%Y-%m-%d %H:%M"), delim, 
                                   tmpf)
    
    return res
    
    
def fetch_hourly( form ):
    ''' Return a fetching of hourly data '''
    sts, ets = get_dates( form )
    stations = get_stations( form )
    delim = get_delimiter( form )
    res = delim.join( ["station","valid","tmpf"] ) + "\n"
    
    cursor.execute("""SELECT station, valid, tair_c_avg from sm_hourly 
    WHERE valid >= '%s 00:00' and valid < '%s 00:00' and station in %s
    ORDER by valid ASC
    """ % (sts.strftime("%Y-%m-%d"), ets.strftime("%Y-%m-%d"), 
           str(tuple(stations))))
    
    for row in cursor:
        if row[2] is None:
            tmpf = -99
        else:
            tmpf = temperature(row[2], 'C').value('F')
        valid = row[1]
        station = row[0]
        
        res += "%s%s%s%s%.1f\n" % (station, delim, 
                                   valid.strftime("%Y-%m-%d %H:%M"), delim, 
                                   tmpf)
    
    return res


if __name__ == '__main__':
    ''' make stuff happen '''
    form = cgi.FieldStorage()
    mode = form.getfirst('mode', 'hourly')
    if mode == 'hourly':
        res = fetch_hourly(form)
    else:
        res = fetch_daily(form)

    todisk = form.getfirst('todisk', 'no')
    if todisk == 'yes':
        sys.stdout.write("Content-type: text/plain\n")
        sys.stdout.write("Content-Disposition: attachment; filename=isusm.txt\n\n") 
    else:
        sys.stdout.write("Content-type: text/plain\n\n")
    sys.stdout.write( res )