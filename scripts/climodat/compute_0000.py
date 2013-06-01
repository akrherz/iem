"""
Compute the statewide average data based on IEMRE analysis
"""
import netCDF4
import psycopg2
import numpy
from pyiem import datatypes, iemre
import sys
import datetime

COOP = psycopg2.connect(database="coop", host='iemdb')
ccursor = COOP.cursor()
POSTGIS = psycopg2.connect(database="postgis", host='iemdb', user='nobody')
pcursor = POSTGIS.cursor()

def do_day(valid):
    nc = netCDF4.Dataset("/mesonet/data/iemre/%s_mw_daily.nc" % (valid.year,))
    for state in ('IA', 'NE', 'MN', 'WI', 'MI', 'OH', 'IN', 'IL', 'MO',
                  'KS', 'KY', 'ND', 'SD'):
        do_state_day(state, valid, nc)
        do_climdiv_day(state, valid, nc)
    nc.close()
        
def do_climdiv_day(stabbr, valid, nc):
    """
    Compute the virtual climate division data as well
    """
    sw_nc = netCDF4.Dataset("/mesonet/data/iemre/climdiv_weights.nc")
    tcnt = iemre.daily_offset(valid)
    for varname in sw_nc.variables.keys():
        if varname in ['lat', 'lon', 'time']:
            continue
        if varname[:2] != stabbr:
            continue
        stid = varname
        sw = sw_nc.variables[stid]
        
        hk = nc.variables['high_tmpk'][tcnt]
        high_tmpk = hk[sw > 0]
        high = datatypes.temperature( numpy.average(high_tmpk), 'K').value("F")
    
        lk = nc.variables['low_tmpk'][tcnt]
        low_tmpk = lk[sw > 0]
        low = datatypes.temperature( numpy.average(low_tmpk), 'K').value("F")
    
        p01d = nc.variables['p01d'][tcnt]
        p01d = p01d[sw > 0]
        precip = numpy.average(p01d) / 25.4
        if precip < 0:
            precip = 0
        
        print '%s %s High: %5.1f Low: %5.1f Precip: %4.2f' % (stid, 
                                                    valid.strftime("%Y-%m-%d"),
                                                    high, low, precip)

        # Now we insert into the proper database!
        ccursor.execute("""DELETE from alldata_%s WHERE station = '%s' 
        and day = '%s'""" % ( stabbr, stid, valid.strftime("%Y-%m-%d"),))
        
        ccursor.execute("""INSERT into alldata_%s 
        (station, day, high, low, precip, snow, snowd, estimated, year, month, 
        sday)
        VALUES ('%s', '%s', %.0f, %.0f, %.2f, %.1f, 0, true, %s, %s, '%s')""" % (
        stabbr, stid, valid.strftime("%Y-%m-%d"), high, low, precip, 
        0, valid.year, valid.month, valid.strftime("%m%d")))

    sw_nc.close()

def do_state_day(stabbr, valid, nc):
    """
    Create the statewide average value based on averages of the IEMRE 
    """
    # Get the bounds of the state
    pcursor.execute("""
    SELECT xmin(ST_Extent(the_geom)), xmax(ST_Extent(the_geom)), 
    ymin(ST_Extent(the_geom)), ymax(ST_Extent(the_geom)) from states
    where state_abbr = %s
    """, (stabbr,))
    row = pcursor.fetchone()
    (ll_i, ll_j) = iemre.find_ij(row[0], row[2])
    (ur_i, ur_j) = iemre.find_ij(row[1], row[3])

    # Open IEMRE
    tcnt = iemre.daily_offset(valid)
    
    high_tmpk = nc.variables['high_tmpk'][tcnt,ll_j:ur_j,ll_i:ur_i]
    high = datatypes.temperature( numpy.average(high_tmpk), 'K').value("F")

    low_tmpk = nc.variables['low_tmpk'][tcnt,ll_j:ur_j,ll_i:ur_i]
    low = datatypes.temperature( numpy.average(low_tmpk), 'K').value("F")

    p01d = nc.variables['p01d'][tcnt,ll_j:ur_j,ll_i:ur_i]
    precip = numpy.average(p01d) / 25.4
    if precip < 0:
        precip = 0
    
    
    print '%s %s OLD High: %5.1f Low: %5.1f Precip: %4.2f' % (stabbr, 
                                                    valid.strftime("%Y-%m-%d"),
                                                high, low, precip)
    
    # get state weights
    sw_nc = netCDF4.Dataset("/mesonet/data/iemre/state_weights.nc")
    sw = sw_nc.variables[stabbr][:]
    sw_nc.close()
    
    hk = nc.variables['high_tmpk'][tcnt]
    high_tmpk = hk[sw>0]
    high = datatypes.temperature( numpy.average(high_tmpk), 'K').value("F")

    lk = nc.variables['low_tmpk'][tcnt]
    low_tmpk = lk[sw>0]
    low = datatypes.temperature( numpy.average(low_tmpk), 'K').value("F")
    
    pk = nc.variables['p01d'][tcnt]
    p01d = pk[sw>0]
    precip = numpy.average(p01d) / 25.4

    print '%s %s NEW High: %5.1f Low: %5.1f Precip: %4.2f' % (stabbr, 
                                                    valid.strftime("%Y-%m-%d"),
                                                high, low, precip)

    
    # Now we insert into the proper database!
    ccursor.execute("""DELETE from alldata_%s WHERE station = '%s0000' 
    and day = '%s'""" % ( stabbr, stabbr, valid.strftime("%Y-%m-%d"),))
    
    ccursor.execute("""INSERT into alldata_%s 
    (station, day, high, low, precip, snow, snowd, estimated, year, month, 
    sday)
    VALUES ('%s0000', '%s', %.0f, %.0f, %.2f, %.1f, 0, true, %s, %s, '%s')""" % (
    stabbr, stabbr, valid.strftime("%Y-%m-%d"), high, low, precip, 
    0, valid.year, valid.month, valid.strftime("%m%d")))
    
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
