"""Climodat Daily Data Estimator

TASK: Given that it takes the QC'd data many months to make the round trip,
      we need to generate estimates so that the climodat reports are more
      useful even if the estimated data has problems

Columns to complete:

 stationid | character(6)     | OK
 day       | date             | OK
 high      | integer          | COOP obs
 low       | integer          | COOP obs
 precip    | double precision | COOP precip
 snow      | double precision | COOP snow
 sday      | character(4)     | OK
 year      | integer          | OK
 month     | smallint         | OK
 snowd     | real             | COOP snowd
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
from pyiem.network import Table as NetworkTable
import datetime
import netCDF4
import numpy as np
from scipy.interpolate import NearestNDInterpolator
import psycopg2.extras
COOP = psycopg2.connect(database='coop', host='iemdb')
ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)
IEM = psycopg2.connect(database='iem', host='iemdb')
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)

state = sys.argv[1]

# Pre-compute the grid location of each climate site
nt = NetworkTable("%sCLIMATE" % (state.upper(),))
for sid in nt.sts.keys():
    i, j = iemre.find_ij(nt.sts[sid]['lon'], nt.sts[sid]['lat'])
    nt.sts[sid]['gridi'] = i
    nt.sts[sid]['gridj'] = j
    for key in ['high', 'low', 'precip', 'snow', 'snowd']:
        nt.sts[sid][key] = None


def estimate_precip(ts):
    """Estimate precipitation based on IEMRE"""
    idx = iemre.daily_offset(ts)
    nc = netCDF4.Dataset("/mesonet/data/iemre/%s_mw_daily.nc" % (ts.year, ),
                         'r')
    grid = nc.variables['p01d_12z'][idx, :, :] / 25.4
    nc.close()

    for sid in nt.sts.keys():
        precip = grid[nt.sts[sid]['gridj'], nt.sts[sid]['gridi']]
        # denote trace
        if precip > 0 and precip < 0.01:
            nt.sts[sid]['precip'] = 0.0001
        elif precip < 0:
            nt.sts[sid]['precip'] = 0
        elif np.isnan(precip):
            nt.sts[sid]['precip'] = 0
        else:
            nt.sts[sid]['precip'] = "%.2f" % (precip,)


def estimate_snow(ts):
    """Estimate the Snow based on COOP reports"""
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
        lats.append(row['lat'])
        lons.append(row['lon'])
        snow.append(row['snow'])
        snowd.append(row['snowd'])

    if len(lats) < 5:
        for sid in nt.sts.keys():
            nt.sts[sid]['snow'] = 0
            nt.sts[sid]['snowd'] = 0
        return

    # Create the analysis
    nn = NearestNDInterpolator((np.array(lons), np.array(lats)),
                               np.array(snow))
    xi, yi = np.meshgrid(iemre.XAXIS, iemre.YAXIS)
    snowgrid = nn(xi, yi)
    nn = NearestNDInterpolator((np.array(lons), np.array(lats)),
                               np.array(snowd))
    xi, yi = np.meshgrid(iemre.XAXIS, iemre.YAXIS)
    snowdgrid = nn(xi, yi)

    for sid in nt.sts.keys():
        snow = snowgrid[nt.sts[sid]['gridj'], nt.sts[sid]['gridi']]
        # denote trace
        if snow > 0 and snow < 0.1:
            nt.sts[sid]['snow'] = 0.0001
        elif snow < 0:
            nt.sts[sid]['snow'] = 0
        elif np.isnan(snow):
            nt.sts[sid]['snow'] = 0
        else:
            nt.sts[sid]['snow'] = "%.1f" % (snow, )

        snowd = snowdgrid[nt.sts[sid]['gridj'], nt.sts[sid]['gridi']]
        # denote trace
        if snowd > 0 and snowd < 0.1:
            nt.sts[sid]['snowd'] = 0.0001
        elif snowd < 0:
            nt.sts[sid]['snowd'] = 0
        elif np.isnan(snowd):
            nt.sts[sid]['snowd'] = 0
        else:
            nt.sts[sid]['snowd'] = "%.1f" % (snowd,)


def estimate_hilo(ts):
    """Estimate the High and Low Temperature based on gridded data"""
    # Query Obs
    # Query Obs
    highs = []
    lows = []
    lats = []
    lons = []
    icursor.execute("""
        SELECT ST_x(s.geom) as lon, ST_y(s.geom) as lat, max_tmpf, min_tmpf
        from summary_%s c, stations s WHERE day = '%s' and
        s.network in ('IA_COOP', 'MN_COOP', 'WI_COOP', 'IL_COOP', 'MO_COOP',
        'KS_COOP', 'NE_COOP', 'SD_COOP', 'ND_COOP', 'KY_COOP', 'MI_COOP',
        'OH_COOP') and c.iemid = s.iemid
        and max_tmpf > -50 and max_tmpf < 130 and
        min_tmpf < 90 and min_tmpf > -60
    """ % (ts.year, ts.strftime("%Y-%m-%d")))
    for row in icursor:
        lats.append(row['lat'])
        lons.append(row['lon'])
        highs.append(row['max_tmpf'])
        lows.append(row['min_tmpf'])

    if len(lats) < 5:
        print 'WARNING: less than 5 temperature obs were found!'
        for sid in nt.sts.keys():
            nt.sts[sid]['high'] = 0
            nt.sts[sid]['low'] = 0
        return

    # Create the analysis
    nn = NearestNDInterpolator((np.array(lons), np.array(lats)),
                               np.array(highs))
    xi, yi = np.meshgrid(iemre.XAXIS, iemre.YAXIS)
    highgrid = nn(xi, yi)

    nn = NearestNDInterpolator((np.array(lons), np.array(lats)),
                               np.array(lows))
    xi, yi = np.meshgrid(iemre.XAXIS, iemre.YAXIS)
    lowgrid = nn(xi, yi)

    for sid in nt.sts.keys():
        high = highgrid[nt.sts[sid]['gridj'], nt.sts[sid]['gridi']]
        if not np.isnan(high):
            nt.sts[sid]['high'] = "%.0f" % (high,)
        low = lowgrid[nt.sts[sid]['gridj'], nt.sts[sid]['gridi']]
        if not np.isnan(low):
            nt.sts[sid]['low'] = "%.0f" % (low,)


def commit(ts):
    """
    Inject into the database!
    """
    # Remove old entries
    ccursor.execute("""
        DELETE from alldata_%s WHERE day = '%s'
    """ % (state.lower(), ts.strftime("%Y-%m-%d")))
    if ccursor.rowcount > 0:
        print 'Removed %s rows from alldata_%s table' % (ccursor.rowcount,
                                                         state.lower())
    # Inject!
    for sid in nt.sts.keys():
        if sid[2] == 'C' or sid[2:] == '0000':
            continue
        sql = """
            INSERT into alldata_"""+state+""" (station, day, high, low,
            precip, snow, sday, year, month, snowd, estimated) values (%s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, 't')"""
        args = (sid, ts, nt.sts[sid]['high'], nt.sts[sid]['low'],
                nt.sts[sid]['precip'], nt.sts[sid]['snow'],
                ts.strftime("%m%d"), ts.year, ts.month, nt.sts[sid]['snowd'])
        ccursor.execute(sql, args)


def main():
    """main()"""
    if len(sys.argv) == 5:
        ts = datetime.date(int(sys.argv[2]), int(sys.argv[3]),
                           int(sys.argv[4]))
    else:
        ts = datetime.date.today()
    estimate_precip(ts)
    estimate_snow(ts)
    estimate_hilo(ts)
    commit(ts)

if __name__ == '__main__':
    ''' See how we are called '''
    main()
    ccursor.close()
    COOP.commit()
    COOP.close()
    icursor.close()
    IEM.commit()
    IEM.close()
