"""
Climodat Daily Data Estimator

TASK: Given that it takes the QC'd data many months to make the round trip,
      we need to generate estimates so that the climodat reports are more
      useful even if the estimated data has problems

Columns to complete:

 stationid | character(6)     | OK
 day       | date             | OK
 high      | integer          | Natgrid ASOS+AWOS
 low       | integer          | Natgrid ASOS+AWOS
 precip    | double precision | Use the WEPP dataset
 snow      | double precision | Natgrid the 12z COOP
 sday      | character(4)     | OK
 year      | integer          | OK
 month     | smallint         | OK
 snowd     | real             | Natgrid the 12z COOP
 estimated | boolean          | true! :)

Steps:
 1) Compute high+low
 2) Compute precip
 3) Look for snow obs
 4) Initialize entries in the table
 5) Run estimate for Iowa Average Site (IA0000)
"""
import sys
from pyiem import iemre
import network
import datetime
import pytz
import numpy
import Ngl
import netCDF4
import os
import psycopg2
import psycopg2.extras
COOP = psycopg2.connect(database='coop', host='iemdb')
ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)
IEM = psycopg2.connect(database='iem', host='iemdb')
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)

state = sys.argv[1]

nt = network.Table("%sCLIMATE" % (state.upper(),))
for sid in nt.sts.keys():
    i,j = iemre.find_ij(nt.sts[sid]['lon'], nt.sts[sid]['lat'])
    nt.sts[sid]['gridi'] = i
    nt.sts[sid]['gridj'] = j
    for key in ['high','low','precip','snow','snowd']:
        nt.sts[sid][key] = None


def hardcode_asos( ts ):
    """
    Hard set the ASOS DSM 
    """

    nt2 = network.Table("IA_ASOS")

    # Get the ASOS data
    icursor.execute("""
       SELECT id, pday, max_tmpf, min_tmpf
       from summary s, stations t WHERE t.iemid = s.iemid and day = '%s' 
       and t.network in ('IA_ASOS') and pday >= 0 and min_tmpf < 99 
       and max_tmpf > -99 ORDER by id ASC""" % (ts.strftime("%Y-%m-%d")))
    for row in icursor:
        cid = nt2.sts[row['id']]['climate_site']
        print ("%s=>P E: %4s Ob: %.2f H E: %4s Ob: %3.0f "
               +"L E: %4s Ob: %3.0f") % (row['id'],
               nt.sts[cid]['precip'], row['pday'],
               nt.sts[cid]['high'], row['max_tmpf'],
               nt.sts[cid]['low'], row['min_tmpf'])
        nt.sts[cid]['precip'] = "%.2f" % (row['pday'],)
        nt.sts[cid]['high'] = "%.0f" % (row['max_tmpf'],)
        nt.sts[cid]['low'] = "%.0f" % (row['min_tmpf'],)


def estimate_precip( ts ):
    """
    Estimate precipitation based on IEMRE, ouch
    """
    fn = "/mesonet/data/iemre/%s_mw_hourly.nc" % (ts.year,)
    if not os.path.isfile(fn):
        print 'Missing netcdf %s analysis!' % (fn,)
        return
    nc = netCDF4.Dataset(fn, 'r')
    precip = nc.variables['p01m']
    # Figure out what offsets we care about!
    ts0 = datetime.datetime(ts.year, ts.month, ts.day, 12, 0)
    ts0 = ts0.replace(tzinfo=pytz.timezone("America/Chicago"))
    ts0 = ts0.replace(hour=0)
    ts1 = ts0 + datetime.timedelta(hours=24)

    offset0 = iemre.hourly_offset(ts0)
    offset1 = iemre.hourly_offset(ts1)
    
    data = numpy.sum( precip[offset0:offset1], 0 )
    # Gross QC check
    data = numpy.where( data > 1000.0, 0, data)
    for sid in nt.sts.keys():
        j = nt.sts[sid]['gridj']
        i = nt.sts[sid]['gridi']
        nt.sts[sid]['precip'] = "%.2f" % (data[j,i] / 25.4,)

    nc.close()

def estimate_snow( ts ):
    """
    Estimate the Snow
    """
    # Query Obs
    snowd = []
    snow = []
    lats = []
    lons = []
    icursor.execute("""
       SELECT ST_x(s.geom) as lon, ST_y(s.geom) as lat, snow, snowd
       from summary_%s c, stations s WHERE day = '%s' and 
       s.network in ('IA_COOP', 'MN_COOP', 'WI_COOP', 'IL_COOP', 'MO_COOP',
        'KS_COOP', 'NE_COOP', 'SD_COOP', 'ND_COOP', 'KY_COOP', 'MI_COOP',
        'OH_COOP') and c.iemid = s.iemid 
       and snowd >= 0""" % (ts.year, ts.strftime("%Y-%m-%d")))
    for row in icursor:
        lats.append( row['lat'] )
        lons.append( row['lon'] )
        snow.append( row['snow'] )
        snowd.append( row['snowd'] )

    if len(lats) < 5: # No data!
        for sid in nt.sts.keys():
            nt.sts[sid]['snow'] = 0
            nt.sts[sid]['snowd'] = 0
        return


    # Create the analysis
    snowA = Ngl.natgrid(lons, lats, snow, iemre.XAXIS, iemre.YAXIS)
    snowdA = Ngl.natgrid(lons, lats, snowd, iemre.XAXIS, iemre.YAXIS)

    for sid in nt.sts.keys():
        snowfall = snowA[nt.sts[sid]['gridi'], nt.sts[sid]['gridj']]
        snowdepth = snowdA[nt.sts[sid]['gridi'], nt.sts[sid]['gridj']]
        if snowfall > 0 and snowfall < 0.1:
            nt.sts[sid]['snow'] = 0.0001
        elif snowfall < 0:
            nt.sts[sid]['snow'] = 0
        elif numpy.isnan(snowfall):
            nt.sts[sid]['snow'] = 0
        else:
            nt.sts[sid]['snow'] = "%.1f" % (snowfall,)
        if snowdepth > 0 and snowdepth < 0.1:
            nt.sts[sid]['snowd'] = 0.0001
        elif snowdepth < 0:
            nt.sts[sid]['snowd'] = 0
        elif numpy.isnan(snowdepth):
            nt.sts[sid]['snowd'] = 0
        else:
            nt.sts[sid]['snowd'] = "%.1f" % (snowdepth,)

def estimate_hilo( ts ):
    """
    Estimate the High and Low Temperature based on gridded data
    """
    # Query Obs
    highs = []
    lows = []
    lats = []
    lons = []
    icursor.execute("""
       SELECT ST_x(s.geom) as lon, ST_y(s.geom) as lat, max_tmpf, min_tmpf
       from summary_%s c, stations s WHERE day = '%s' 
       and s.network in ('AWOS','IA_ASOS', 'MN_ASOS', 'WI_ASOS', 
       'IL_ASOS', 'MO_ASOS',
        'KS_ASOS', 'NE_ASOS', 'SD_ASOS', 'ND_ASOS', 'KY_ASOS', 'MI_ASOS',
        'OH_ASOS') and c.iemid = s.iemid
       and max_tmpf > -90 and min_tmpf < 90""" % (ts.year, 
                                                  ts.strftime("%Y-%m-%d")))
    for row in icursor:
        lats.append( row['lat'] )
        lons.append( row['lon'] )
        highs.append( row['max_tmpf'] )
        lows.append( row['min_tmpf'] )

    if len(highs) < 5:
        print 'estimate_hilo() only found %s observations' % (len(highs),)
        return

    # Create the analysis
    highA = Ngl.natgrid(lons, lats, highs, iemre.XAXIS, iemre.YAXIS)
    lowA = Ngl.natgrid(lons, lats, lows, iemre.XAXIS, iemre.YAXIS)

    for sid in nt.sts.keys():
        nt.sts[sid]['high'] = "%.0f" % (
                            highA[nt.sts[sid]['gridi'], nt.sts[sid]['gridj']])
        nt.sts[sid]['low'] = "%.0f" % (
                            lowA[nt.sts[sid]['gridi'], nt.sts[sid]['gridj']])

def commit( ts ):
    """
    Inject into the database!
    """
    # Remove old entries
    sql = "DELETE from alldata_%s WHERE day = '%s'" % (state.lower(), 
                                                    ts.strftime("%Y-%m-%d"),)
    ccursor.execute( sql )
    if ccursor.rowcount > 0:
        print 'Removed %s rows from alldata_%s table' % (ccursor.rowcount,
                                                         state.lower())
    # Inject!
    for sid in nt.sts.keys():
        sql = """INSERT into alldata_"""+state+""" (station, day, high, low, 
        precip, snow, sday, year, month, snowd, estimated) values (%s, %s, 
        %s, %s, %s, %s, %s, %s, %s, %s, 't')"""
        args = (sid, ts, nt.sts[sid]['high'], nt.sts[sid]['low'], 
                nt.sts[sid]['precip'], nt.sts[sid]['snow'], ts.strftime("%m%d"), 
                ts.year, ts.month, nt.sts[sid]['snowd'])
        ccursor.execute( sql, args )


if __name__ == '__main__':
    ''' See how we are called '''
    if len(sys.argv) == 5:
        ts = datetime.date( int(sys.argv[2]), int(sys.argv[3]), 
                                   int(sys.argv[4]))
    else:
        ts = datetime.date.today() - datetime.timedelta(days=1)
    estimate_hilo( ts )
    estimate_precip(ts )
    estimate_snow(ts )
    if state.upper() == 'IA':
        hardcode_asos(ts )
    commit( ts )
    ccursor.close()
    COOP.commit()
    COOP.close()
    icursor.close()
    IEM.commit()
    IEM.close()
    