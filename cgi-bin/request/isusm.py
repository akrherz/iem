#!/usr/bin/env python
''' 
 Download interface for ISU-SM data
'''
import cgi
import datetime
import psycopg2
import sys
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
    
    res = delim.join( ["station","valid","high", "low", "solar", "precip",
                       "sped", "gust", "et", "soil04t", "soil12t", "soil24t", "soil50t",
                       "soil12vwc", "soil24vwc", "soil50vwc",] ) + "\n"
    
    sql = """SELECT station, valid, tair_c_max, tair_c_min, slrmj_tot,
    rain_mm_tot, dailyet, tsoil_c_avg, t12_c_avg, t24_c_avg, t50_c_avg,
    vwc_12_avg, vwc_24_avg, vwc_50_avg, ws_mps_s_wvt, ws_mps_max
    from sm_daily 
    WHERE valid >= '%s 00:00' and valid < '%s 00:00' and station in %s
    ORDER by valid ASC
    """ % (sts.strftime("%Y-%m-%d"), ets.strftime("%Y-%m-%d"), 
           str(tuple(stations)))
    cursor.execute(sql)
    
    for row in cursor:
        valid = row[1]
        station = row[0]
        high = temperature(row[2], 'C').value('F') if row[2] is not None else -99
        low = temperature(row[3], 'C').value('F') if row[3] is not None else -99
        precip = row[5] / 24.5 if row[5] > 0 else 0
        et = row[6] / 24.5 if row[6] > 0 else 0
        tsoil04t = temperature(row[7], 'C').value('F') if row[7] is not None else -99
        tsoil12t = temperature(row[8], 'C').value('F') if row[8] is not None else -99
        tsoil24t = temperature(row[9], 'C').value('F') if row[9] is not None else -99
        tsoil50t = temperature(row[10], 'C').value('F') if row[10] is not None else -99
        tsoil12vwc = row[11] if row[11] is not None else -99
        tsoil24vwc = row[12] if row[12] is not None else -99
        tsoil50vwc = row[13] if row[13] is not None else -99
        speed = row[14] * 2.23 if row[14] is not None else -99
        gust = row[15] * 2.23 if row[15] is not None else -99
        
        values = [station, valid.strftime("%Y-%m-%d"), high, low, row[4],
                  precip, speed, gust, et, tsoil04t, tsoil12t, tsoil24t, tsoil50t,
                  tsoil12vwc, tsoil24vwc, tsoil50vwc]
        res += delim.join(map(str,values)) + "\n"
    
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