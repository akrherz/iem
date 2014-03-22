"""
 Compute the statewide and climate division average data based on gridded
 COOP obs
"""
import netCDF4
import psycopg2
import numpy as np
from scipy.interpolate import NearestNDInterpolator
from pyiem import iemre
import sys
import datetime

COOP = psycopg2.connect(database="coop", host='iemdb')
ccursor = COOP.cursor()

def do_day(valid):
    ''' Process a day please '''
    
    ccursor.execute("""
    SELECT ST_x(geom), ST_y(geom), high, low, precip, snow, snowd from
    alldata a JOIN stations t on (t.id = a.station) 
    where t.network ~* 'CLIMATE' and day = '%s' and substr(station,2,1) != 'C'
    and substr(station,2,4) != '0000' and high is not null and
    precip is not null
    """ % (valid.strftime("%Y-%m-%d"),))
    lats = []
    lons = []
    highs= []
    lows = []
    precip = []
    snow = []
    snowd = []
    for row in ccursor:
        lats.append( row[1] )
        lons.append( row[0] )
        highs.append( row[2] )
        lows.append( row[3] )
        precip.append( row[4] )
        snow.append( row[5] )
        snowd.append( row[6] )
    
    
    nn = NearestNDInterpolator((np.array(lons), np.array(lats)), np.array(snowd))
    xi, yi = np.meshgrid(iemre.XAXIS, iemre.YAXIS)
    snowdgrid = nn(xi, yi)

    nn = NearestNDInterpolator((np.array(lons), np.array(lats)), np.array(snow))
    snowgrid = nn(xi, yi)
   
    nn = NearestNDInterpolator((np.array(lons), np.array(lats)), np.array(precip))
    precipgrid = nn(xi, yi)
   
    nn = NearestNDInterpolator((np.array(lons), np.array(lats)), np.array(highs))
    highgrid = nn(xi, yi)

    nn = NearestNDInterpolator((np.array(lons), np.array(lats)), np.array(lows))
    lowgrid = nn(xi, yi)
    
    for state in ('IA', 'NE', 'MN', 'WI', 'MI', 'OH', 'IN', 'IL', 'MO',
                  'KS', 'KY', 'ND', 'SD'):
        do_state_day(state, valid, highgrid, lowgrid, precipgrid, snowgrid,
                     snowdgrid)
        do_climdiv_day(state, valid, highgrid, lowgrid, precipgrid, snowgrid,
                     snowdgrid)
       
       
        
def do_climdiv_day(stabbr, valid, highgrid, lowgrid, precipgrid, snowgrid,
                     snowdgrid):
    """
    Compute the virtual climate division data as well
    """
    sw_nc = netCDF4.Dataset("/mesonet/data/iemre/climdiv_weights.nc")
    for varname in sw_nc.variables.keys():
        if varname in ['lat', 'lon', 'time']:
            continue
        if varname[:2] != stabbr:
            continue
        stid = varname
        sw = sw_nc.variables[stid][:]
        
        high = np.average(highgrid[sw > 0])    
        low = np.average(lowgrid[sw > 0])
        precip = np.average(precipgrid[sw > 0])
        snow = np.average(snowgrid[sw > 0])    
        snowd = np.average(snowdgrid[sw > 0])
        
        print '%s %s High: %5.1f Low: %5.1f Precip: %4.2f' % (stid, 
                                                    valid.strftime("%Y-%m-%d"),
                                                    high, low, precip)

        # Now we insert into the proper database!
        ccursor.execute("""DELETE from alldata_%s WHERE station = '%s' 
        and day = '%s'""" % ( stabbr, stid, valid.strftime("%Y-%m-%d"),))
        
        ccursor.execute("""INSERT into alldata_%s 
        (station, day, high, low, precip, snow, snowd, estimated, year, month, 
        sday)
        VALUES ('%s', '%s', %.0f, %.0f, %.2f, %.1f, %.1f, true, %s, %s, '%s')""" % (
        stabbr, stid, valid.strftime("%Y-%m-%d"), high, low, precip, 
        snow, snowd, valid.year, valid.month, valid.strftime("%m%d")))

    sw_nc.close()

def do_state_day(stabbr, valid, highgrid, lowgrid, precipgrid, snowgrid,
                     snowdgrid):
    """
    Create the statewide average value based on averages of the IEMRE 
    """
    
    # get state weights
    sw_nc = netCDF4.Dataset("/mesonet/data/iemre/state_weights.nc")
    sw = sw_nc.variables[stabbr][:]
    sw_nc.close()
    
    high = np.average(highgrid[sw > 0])    
    low = np.average(lowgrid[sw > 0])
    precip = np.average(precipgrid[sw > 0])
    snow = np.average(snowgrid[sw > 0])    
    snowd = np.average(snowdgrid[sw > 0])

    print '%s %s NEW High: %5.1f Low: %5.1f Precip: %4.2f' % (stabbr, 
                                                    valid.strftime("%Y-%m-%d"),
                                                high, low, precip)

    # Now we insert into the proper database!
    ccursor.execute("""DELETE from alldata_%s WHERE station = '%s0000' 
    and day = '%s'""" % ( stabbr, stabbr, valid.strftime("%Y-%m-%d"),))
    
    ccursor.execute("""INSERT into alldata_%s 
    (station, day, high, low, precip, snow, snowd, estimated, year, month, 
    sday)
    VALUES ('%s0000', '%s', %.0f, %.0f, %.2f, %.1f, %.1f, true, %s, %s, '%s')""" % (
    stabbr, stabbr, valid.strftime("%Y-%m-%d"), high, low, precip, 
    snow, snowd, valid.year, valid.month, valid.strftime("%m%d")))
    
if __name__ == '__main__':
    if len(sys.argv) == 4:
        do_day( datetime.datetime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])))
    elif len(sys.argv) == 3:
        sts = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]), 1)
        ets = sts + datetime.timedelta(days=35)
        ets = ets.replace(day=1)
        now = sts
        while now < ets:
            do_day( now )
            now += datetime.timedelta(days=1)
    else:
        do_day( datetime.datetime.now() - datetime.timedelta(days=1))
    
    ccursor.close()
    COOP.commit()
