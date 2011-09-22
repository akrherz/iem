"""
Compute the statewide average data based on IEMRE analysis
"""
try:
    import netCDF4 as netCDF3
except:
    import netCDF3
import iemdb
import numpy
import iemre
import mesonet
import sys
import mx.DateTime
COOP = iemdb.connect("coop", bypass=True)
ccursor = COOP.cursor()
POSTGIS = iemdb.connect("postgis", bypass=True)
pcursor = POSTGIS.cursor()

def do_day(valid):
    for state in ('IA','MN','WI','MI','OH','IN','IL','MO','KS','KY','ND','SD'):
        do_state_day(state, valid)
        do_climdiv_day(state, valid)
        
def do_climdiv_day(stabbr, valid):
    """
    Compute the virtual climate division data as well
    """
    pcursor.execute("""
    SELECT stdiv_, xmin(ST_Extent(the_geom)), xmax(ST_Extent(the_geom)), 
    ymin(ST_Extent(the_geom)), ymax(ST_Extent(the_geom)) from climate_div
    where st = %s
    """, (stabbr,))
    for row in pcursor:
        stid = "%sC0%s" % (st, str(row[0])[-2:])
        (ll_i, ll_j) = iemre.find_ij(row[1], row[3])
        (ur_i, ur_j) = iemre.find_ij(row[2], row[4])
            # Open IEMRE
        nc = netCDF3.Dataset("/mesonet/data/iemre/%s_mw_daily.nc" % (valid.year,))
        tcnt = int((valid - mx.DateTime.DateTime(valid.year,1,1)).days)
    
        high_tmpk = nc.variables['high_tmpk'][tcnt,ll_j:ur_j,ll_i:ur_i]
        high = mesonet.k2f( numpy.average(high_tmpk) )
    
        low_tmpk = nc.variables['low_tmpk'][tcnt,ll_j:ur_j,ll_i:ur_i]
        low = mesonet.k2f( numpy.average(low_tmpk) )
    
        p01d = nc.variables['p01d'][tcnt,ll_j:ur_j,ll_i:ur_i]
        precip = numpy.average(p01d) / 25.4
        if precip < 0:
            precip = 0
        
        nc.close()
        
        print '%s %s High: %5.1f Low: %5.1f Precip: %4.2f' % (stid, valid.strftime("%Y-%m-%d"),
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

def do_state_day(stabbr, valid):
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
    nc = netCDF3.Dataset("/mesonet/data/iemre/%s_mw_daily.nc" % (valid.year,))
    tcnt = int((valid - mx.DateTime.DateTime(valid.year,1,1)).days)

    high_tmpk = nc.variables['high_tmpk'][tcnt,ll_j:ur_j,ll_i:ur_i]
    high = mesonet.k2f( numpy.average(high_tmpk) )

    low_tmpk = nc.variables['low_tmpk'][tcnt,ll_j:ur_j,ll_i:ur_i]
    low = mesonet.k2f( numpy.average(low_tmpk) )

    p01d = nc.variables['p01d'][tcnt,ll_j:ur_j,ll_i:ur_i]
    precip = numpy.average(p01d) / 25.4
    if precip < 0:
        precip = 0
    
    nc.close()
    
    print '%s %s High: %5.1f Low: %5.1f Precip: %4.2f' % (stabbr, valid.strftime("%Y-%m-%d"),
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
        do_day( mx.DateTime.DateTime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])))
    else:
        do_day( mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=1))
    
    ccursor.close()
    COOP.commit()