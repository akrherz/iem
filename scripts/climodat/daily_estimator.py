"""
Climodat Daily Data Estimator

TASK: Given that it takes the QC'd data many months to make the round trip,
      we need to generate estimates so that the climodat reports are more
      useful even if the estimated data has problems

Columns to complete:

 stationid | character(6)     | OK
 day       | date             | OK
 climoweek | integer          | Merge in from the climoweek relation
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
sys.path.append('../lib/')
import iemplot
import mx.DateTime
import numpy
import Ngl
from pyIEM import iemdb
i = iemdb.iemdb()
coop = i['coop']
wepp = i['wepp']
iem = i['iem']
mesosite = i['mesosite']

delx = (iemplot.IA_EAST - iemplot.IA_WEST) / (iemplot.IA_NX - 1)
dely = (iemplot.IA_NORTH - iemplot.IA_SOUTH) / (iemplot.IA_NY - 1)

# Figure out which stations we care for
stations = {}
rs = mesosite.query("SELECT id, x(geom) as lon, y(geom) as lat from stations WHERE network = 'IACLIMATE' and id != 'IA0000'").dictresult()
for i in range(len(rs)):
    stations[ rs[i]['id'].lower() ] = rs[i]
    # Figure out the gridi, gridy
    y = 0
    while (iemplot.IA_SOUTH + (dely * y)) < rs[i]['lat']:
        y += 1
    stations[ rs[i]['id'].lower() ]['gridy'] = y
    x = 0
    while (iemplot.IA_WEST + (delx * x)) < rs[i]['lon']:
        x += 1
    stations[ rs[i]['id'].lower() ]['gridx'] = x

def hardcode_asos_precip( ts ):
    """
    Hard set the ASOS DSM precip 
    """
    # Figure out the sites we care about
    asos2climate = {}
    rs = mesosite.query("""SELECT id, climate_site from stations
         where network = 'IA_ASOS'""").dictresult()
    for i in range(len(rs)):
        asos2climate[ rs[i]['id'] ] = rs[i]['climate_site'].lower()

    # Get the ASOS precip
    rs = iem.query("""
       SELECT station, pday
       from summary_%s WHERE day = '%s' and network in ('IA_ASOS')
       and pday >= 0 ORDER by station ASC""" % (
       ts.year, ts.strftime("%Y-%m-%d"))).dictresult()
    for i in range(len(rs)):
        cid = asos2climate[rs[i]['station']]
        print '%s - Estimated: %.2f  DSM: %.2f' % (rs[i]['station'],
               stations[cid]['precip'], rs[i]['pday'])
        stations[cid]['precip'] = rs[i]['pday']


def estimate_precip( ts ):
    """
    Estimate precipitation based on IEM Rainfall 
    """
    for id in stations.keys():
        sql = """
    SELECT rainfall from daily_rainfall_%s WHERE
    hrap_i = ( select hrap_i from hrap_utm 
               ORDER by distance( the_geom,
                     transform(geometryfromtext('POINT(%s %s)',4326), 26915)) 
               ASC LIMIT 1 ) and valid = '%s'
        """ % (ts.year,  stations[id]['lon'], stations[id]['lat'],
               ts.strftime("%Y-%m-%d") )
        rs = wepp.query( sql ).dictresult()
        if len(rs) == 0:
            stations[id]['precip'] = 0
        else:
            stations[id]['precip'] = rs[0]['rainfall'] / 25.4

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
       SELECT x(geom) as lon, y(geom) as lat, snow, snowd
       from summary_%s WHERE day = '%s' and 
       network in ('IA_COOP', 'MN_COOP', 'WI_COOP', 'IL_COOP', 'MO_COOP',
        'KS_COOP', 'NE_COOP', 'SD_COOP')
       and snowd >= 0""" % (ts.year, ts.strftime("%Y-%m-%d"))).dictresult()
    for i in range(len(rs)):
        lats.append( rs[i]['lat'] )
        lons.append( rs[i]['lon'] )
        snow.append( rs[i]['snow'] )
        snowd.append( rs[i]['snowd'] )

    if len(lats) < 5: # No data!
        for id in stations.keys():
            stations[id]['snow'] = 0
            stations[id]['snowd'] = 0
        return

    # Create axis
    xaxis = iemplot.IA_WEST + delx * numpy.arange(0, iemplot.IA_NX)
    yaxis = iemplot.IA_SOUTH + dely * numpy.arange(0, iemplot.IA_NY)
    # Create the analysis
    snowA = Ngl.natgrid(lons, lats, snow, xaxis, yaxis)
    snowdA = Ngl.natgrid(lons, lats, snowd, xaxis, yaxis)

    for id in stations.keys():
        snowfall = snowA[stations[id]['gridx'], stations[id]['gridy']]
        snowdepth = snowdA[stations[id]['gridx'], stations[id]['gridy']]
        if snowfall > 0 and snowfall < 0.1:
          stations[id]['snow'] = 0.0001
        elif snowfall < 0:
          stations[id]['snow'] = 0
        else:
          stations[id]['snow'] = snowfall
        if snowdepth > 0 and snowdepth < 0.1:
          stations[id]['snowd'] = 0.0001
        elif snowdepth < 0:
          stations[id]['snowd'] = 0
        else:
          stations[id]['snowd'] = snowdepth

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
       SELECT x(geom) as lon, y(geom) as lat, max_tmpf, min_tmpf
       from summary_%s WHERE day = '%s' and network in ('IA_ASOS', 'AWOS')
       and max_tmpf > -90""" % (ts.year, ts.strftime("%Y-%m-%d"))).dictresult()
    for i in range(len(rs)):
        lats.append( rs[i]['lat'] )
        lons.append( rs[i]['lon'] )
        highs.append( rs[i]['max_tmpf'] )
        lows.append( rs[i]['min_tmpf'] )

    # Create axis
    xaxis = iemplot.IA_WEST + delx * numpy.arange(0, iemplot.IA_NX)
    yaxis = iemplot.IA_SOUTH + dely * numpy.arange(0, iemplot.IA_NY)
    # Create the analysis
    highA = Ngl.natgrid(lons, lats, highs, xaxis, yaxis)
    lowA = Ngl.natgrid(lons, lats, lows, xaxis, yaxis)

    for id in stations.keys():
        stations[id]['high'] = highA[stations[id]['gridx'], stations[id]['gridy']]
        stations[id]['low'] = lowA[stations[id]['gridx'], stations[id]['gridy']]

def commit( ts ):
    """
    Inject into the database!
    """
    # Remove old entries
    sql = "DELETE from alldata WHERE day = '%s'" % (ts.strftime("%Y-%m-%d"),)
    coop.query( sql )
    # Inject!
    for id in stations.keys():
        sql = "INSERT into alldata values ('%s', '%s', (select climoweek from climoweek where sday = '%s'), %.0f, %.0f, %.2f, %.1f, '%s', %s, %s, %.0f, 't')" % (id, ts.strftime("%Y-%m-%d"), ts.strftime("%m%d"), 
        stations[id]['high'], stations[id]['low'], stations[id]['precip'],
        stations[id]['snow'],
        ts.strftime("%m%d"), ts.year, ts.month, stations[id]['snowd'])
        if os.environ['USER'] != 'akrherz':
            coop.query( sql )
       


if __name__ == '__main__':
    if len(sys.argv) == 4:
        ts = mx.DateTime.DateTime( int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
    else:
        ts = mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=1)
    estimate_hilo( ts )
    estimate_precip( ts )
    estimate_snow( ts )
    hardcode_asos_precip( ts )
    commit( ts )
