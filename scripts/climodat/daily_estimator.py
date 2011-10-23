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
 5) Run estimate for Iowa Average Site (ia0000)
"""
import sys, os
import iemre
import network
import iemplot
import mx.DateTime
import numpy
import Ngl
try:
    import netCDF4 as netCDF3
except:
    import netCDF3
from pyIEM import iemdb
i = iemdb.iemdb()
coop = i['coop']
wepp = i['wepp']
iem = i['iem']
mesosite = i['mesosite']

state = sys.argv[1]

nt = network.Table("%sCLIMATE" % (state.upper(),))
for id in nt.sts.keys():
    i,j = iemre.find_ij(nt.sts[id]['lon'], nt.sts[id]['lat'])
    nt.sts[id]['gridi'] = i
    nt.sts[id]['gridj'] = j
    for key in ['high','low','precip','snow','snowd']:
        nt.sts[id][key] = None


def hardcode_asos( ts ):
    """
    Hard set the ASOS DSM 
    """

    nt2 = network.Table("IA_ASOS")

    # Get the ASOS data
    rs = iem.query("""
       SELECT id, pday, max_tmpf, min_tmpf
       from summary_%s s, stations t WHERE t.iemid = s.iemid and day = '%s' and t.network in ('IA_ASOS')
       and pday >= 0 and min_tmpf < 99 and max_tmpf > -99 ORDER by id ASC""" % (
       ts.year, ts.strftime("%Y-%m-%d"))).dictresult()
    for i in range(len(rs)):
        cid = nt2.sts[rs[i]['id']]['climate_site']
        print '%s - Precip: %.2f  DSM: %.2f High: %.1f DSM: %s Low: %.1f DSM: %s' % (rs[i]['id'],
               nt.sts[cid]['precip'], rs[i]['pday'],
               nt.sts[cid]['high'], rs[i]['max_tmpf'],
               nt.sts[cid]['low'], rs[i]['min_tmpf']
        )
        nt.sts[cid]['precip'] = rs[i]['pday']
        nt.sts[cid]['high'] = rs[i]['max_tmpf']
        nt.sts[cid]['low'] = rs[i]['min_tmpf']


def estimate_precip( ts ):
    """
    Estimate precipitation based on IEMRE, ouch
    """
    nc = netCDF3.Dataset("/mesonet/data/iemre/%s_mw_hourly.nc" % (ts.year,), 'r')
    precip = nc.variables['p01m']
    # Figure out what offsets we care about!
    ts0 = ts + mx.DateTime.RelativeDateTime(hour=7)
    offset0 = int(( ts0 - (ts + mx.DateTime.RelativeDateTime(month=1,day=1,hour=0))).hours) - 1
    ts1 = ts + mx.DateTime.RelativeDateTime(days=1,hour=6)
    offset1 = int(( ts1 - (ts + mx.DateTime.RelativeDateTime(month=1,day=1,hour=0))).hours) - 1
    data = numpy.sum( precip[offset0:offset1], 0 )
    for id in nt.sts.keys():
        j = nt.sts[id]['gridj']
        i = nt.sts[id]['gridi']
        nt.sts[id]['precip'] = data[j,i] / 25.4

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
    rs = iem.query("""
       SELECT x(s.geom) as lon, y(s.geom) as lat, snow, snowd
       from summary_%s c, stations s WHERE day = '%s' and 
       s.network in ('IA_COOP', 'MN_COOP', 'WI_COOP', 'IL_COOP', 'MO_COOP',
        'KS_COOP', 'NE_COOP', 'SD_COOP', 'ND_COOP', 'KY_COOP', 'MI_COOP',
        'OH_COOP') and c.iemid = s.iemid 
       and snowd >= 0""" % (ts.year, ts.strftime("%Y-%m-%d"))).dictresult()
    for i in range(len(rs)):
        lats.append( rs[i]['lat'] )
        lons.append( rs[i]['lon'] )
        snow.append( rs[i]['snow'] )
        snowd.append( rs[i]['snowd'] )

    if len(lats) < 5: # No data!
        for id in nt.sts.keys():
            nt.sts[id]['snow'] = 0
            nt.sts[id]['snowd'] = 0
        return


    # Create the analysis
    snowA = Ngl.natgrid(lons, lats, snow, iemre.XAXIS, iemre.YAXIS)
    snowdA = Ngl.natgrid(lons, lats, snowd, iemre.XAXIS, iemre.YAXIS)

    for id in nt.sts.keys():
        snowfall = snowA[nt.sts[id]['gridi'], nt.sts[id]['gridj']]
        snowdepth = snowdA[nt.sts[id]['gridi'], nt.sts[id]['gridj']]
        if snowfall > 0 and snowfall < 0.1:
          nt.sts[id]['snow'] = 0.0001
        elif snowfall < 0:
          nt.sts[id]['snow'] = 0
        elif numpy.isnan(snowfall):
          nt.sts[id]['snow'] = 0
        else:
          nt.sts[id]['snow'] = snowfall
        if snowdepth > 0 and snowdepth < 0.1:
          nt.sts[id]['snowd'] = 0.0001
        elif snowdepth < 0:
          nt.sts[id]['snowd'] = 0
        elif numpy.isnan(snowdepth):
          nt.sts[id]['snowd'] = 0
        else:
          nt.sts[id]['snowd'] = snowdepth

def estimate_hilo( ts ):
    """
    Estimate the High and Low Temperature based on gridded data
    """
    # Query Obs
    highs = []
    lows = []
    lats = []
    lons = []
    rs = iem.query("""
       SELECT x(s.geom) as lon, y(s.geom) as lat, max_tmpf, min_tmpf
       from summary_%s c, stations s WHERE day = '%s' and s.network in ('AWOS','IA_ASOS', 'MN_ASOS', 'WI_ASOS', 
       'IL_ASOS', 'MO_ASOS',
        'KS_ASOS', 'NE_ASOS', 'SD_ASOS', 'ND_ASOS', 'KY_ASOS', 'MI_ASOS',
        'OH_ASOS') and c.iemid = s.iemid
       and max_tmpf > -90 and min_tmpf < 90""" % (ts.year, ts.strftime("%Y-%m-%d"))).dictresult()
    for i in range(len(rs)):
        lats.append( rs[i]['lat'] )
        lons.append( rs[i]['lon'] )
        highs.append( rs[i]['max_tmpf'] )
        lows.append( rs[i]['min_tmpf'] )

    # Create the analysis
    highA = Ngl.natgrid(lons, lats, highs, iemre.XAXIS, iemre.YAXIS)
    lowA = Ngl.natgrid(lons, lats, lows, iemre.XAXIS, iemre.YAXIS)

    for id in nt.sts.keys():
        nt.sts[id]['high'] = highA[nt.sts[id]['gridi'], nt.sts[id]['gridj']]
        nt.sts[id]['low'] = lowA[nt.sts[id]['gridi'], nt.sts[id]['gridj']]

def commit( ts ):
    """
    Inject into the database!
    """
    # Remove old entries
    sql = "DELETE from alldata_%s WHERE day = '%s'" % (state.lower(), ts.strftime("%Y-%m-%d"),)
    coop.query( sql )
    # Inject!
    for id in nt.sts.keys():
        sql = """INSERT into alldata_%s(station, day, high, low, precip, snow, 
        sday, year, month, snowd, estimated) values ('%s', '%s', 
        %.0f, %.0f, %.2f, %.1f, 
        '%s', %s, %s, %.0f, 't')""" % (state, id, ts.strftime("%Y-%m-%d"), 
        nt.sts[id]['high'], nt.sts[id]['low'], nt.sts[id]['precip'],
        nt.sts[id]['snow'],
        ts.strftime("%m%d"), ts.year, ts.month, nt.sts[id]['snowd'])
        coop.query( sql )
       


if __name__ == '__main__':
    if len(sys.argv) == 5:
        ts = mx.DateTime.DateTime( int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
    else:
        ts = mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=1)
    estimate_hilo( ts )
    estimate_precip(ts )
    estimate_snow(ts )
    if state.upper() == 'IA':
        hardcode_asos(ts )
    commit( ts )
