"""
 Grid the daily data onto a midwest grid for IEMRE
"""
import sys
import netCDF4
import numpy as np
import datetime
import psycopg2
import pytz
from pyiem import iemre, datatypes
from psycopg2.extras import DictCursor
from scipy.interpolate import NearestNDInterpolator

pgconn = psycopg2.connect(database='iem', host='iemdb', user='nobody')
cursor = pgconn.cursor(cursor_factory=DictCursor)


def generic_gridder(rs, idx):
    """
    Generic gridding algorithm for easy variables
    """
    lats = []
    lons = []
    vals = []
    for row in rs:
        if row[idx] is not None:
            lats.append(row['lat'])
            lons.append(row['lon'])
            vals.append(row[idx])
    if len(vals) < 4:
        print(("Only %s observations found for %s, won't grid"
               ) % (len(vals), idx))
        return None

    nn = NearestNDInterpolator((np.array(lons), np.array(lats)),
                               np.array(vals))
    xi, yi = np.meshgrid(iemre.XAXIS, iemre.YAXIS)
    grid = nn(xi, yi)

    return grid


def do_precip(nc, ts):
    """Compute the 6 UTC to 6 UTC precip

    We need to be careful here as the timestamp sent to this app is today,
    we are actually creating the analysis for yesterday
    """
    sts = datetime.datetime(ts.year, ts.month, ts.day, 6)
    sts = sts.replace(tzinfo=pytz.timezone("UTC"))
    ets = sts + datetime.timedelta(hours=24)
    offset = iemre.daily_offset(ts)
    offset1 = iemre.hourly_offset(sts)
    offset2 = iemre.hourly_offset(ets)
    print(("p01d      for %s [idx:%s] %s(%s)->%s(%s)"
           ) % (ts, offset, sts.strftime("%Y%m%d%H"), offset1,
                ets.strftime("%Y%m%d%H"), offset2))
    hnc = netCDF4.Dataset("/mesonet/data/iemre/%s_mw_hourly.nc" % (sts.year,))
    phour = np.sum(hnc.variables['p01m'][offset1:offset2, :, :], 0)
    nc.variables['p01d'][offset] = phour
    hnc.close()


def do_precip12(nc, ts):
    """Compute the 24 Hour precip at 12 UTC, we do some more tricks though"""
    offset = iemre.daily_offset(ts)
    ets = datetime.datetime(ts.year, ts.month, ts.day, 12)
    ets = ets.replace(tzinfo=pytz.timezone("UTC"))
    sts = ets - datetime.timedelta(hours=24)
    offset1 = iemre.hourly_offset(sts)
    offset2 = iemre.hourly_offset(ets)
    print(("p01d_12z  for %s [idx:%s] %s(%s)->%s(%s)"
           ) % (ts, offset, sts.strftime("%Y%m%d%H"), offset1,
                ets.strftime("%Y%m%d%H"), offset2))
    hnc = netCDF4.Dataset("/mesonet/data/iemre/%s_mw_hourly.nc" % (ts.year,))
    phour = np.sum(hnc.variables['p01m'][offset1:offset2, :, :], 0)
    nc.variables['p01d_12z'][offset] = phour
    hnc.close()


def grid_day12(nc, ts):
    """Use the COOP data for gridding
    """
    offset = iemre.daily_offset(ts)
    print(('12z hi/lo for %s [idx:%s]') % (ts, offset))
    cursor.execute("""
       SELECT ST_x(s.geom) as lon, ST_y(s.geom) as lat,
       (CASE WHEN pday >= 0 then pday else null end) as precipdata,
       (CASE WHEN snow >= 0 then snow else null end) as snowdata,
       (CASE WHEN snowd >= 0 then snowd else null end) as snowddata,
       (CASE WHEN max_tmpf > -50 and max_tmpf < 130
           then max_tmpf else null end) as highdata,
       (CASE WHEN min_tmpf > -50 and min_tmpf < 95
           then min_tmpf else null end) as lowdata
       from summary_%s c, stations s WHERE day = '%s' and
       s.network in ('IA_COOP', 'MN_COOP', 'WI_COOP', 'IL_COOP', 'MO_COOP',
        'KS_COOP', 'NE_COOP', 'SD_COOP', 'ND_COOP', 'KY_COOP', 'MI_COOP',
        'OH_COOP') and c.iemid = s.iemid and
        extract(hour from c.coop_valid) between 4 and 11
        """ % (ts.year, ts.strftime("%Y-%m-%d")))

    if cursor.rowcount > 4:
        res = generic_gridder(cursor, 'highdata')
        nc.variables['high_tmpk_12z'][offset] = datatypes.temperature(
                                                res, 'F').value('K')

        cursor.scroll(0, mode='absolute')
        res = generic_gridder(cursor, 'lowdata')
        nc.variables['low_tmpk_12z'][offset] = datatypes.temperature(
                                            res, 'F').value('K')

        cursor.scroll(0, mode='absolute')
        res = generic_gridder(cursor, 'snowdata')
        nc.variables['snow_12z'][offset] = res * 25.4

        cursor.scroll(0, mode='absolute')
        res = generic_gridder(cursor, 'snowddata')
        nc.variables['snowd_12z'][offset] = res * 25.4
    else:
        print "%s has %02i entries, FAIL" % (ts.strftime("%Y-%m-%d"),
                                             cursor.rowcount)


def grid_day(nc, ts):
    """
    """
    offset = iemre.daily_offset(ts)
    print(('cal hi/lo for %s [idx:%s]') % (ts, offset))
    cursor.execute("""
       SELECT ST_x(s.geom) as lon, ST_y(s.geom) as lat,
       (CASE WHEN pday >= 0 then pday else null end) as precipdata,
       (CASE WHEN max_tmpf > -50 and max_tmpf < 130
           then max_tmpf else null end) as highdata,
       (CASE WHEN min_tmpf > -50 and min_tmpf < 95
           then min_tmpf else null end) as lowdata
       from summary_%s c, stations s WHERE day = '%s' and
       s.network in ('IA_ASOS', 'MN_ASOS', 'WI_ASOS', 'IL_ASOS', 'MO_ASOS',
        'KS_ASOS', 'NE_ASOS', 'SD_ASOS', 'ND_ASOS', 'KY_ASOS', 'MI_ASOS',
        'OH_ASOS', 'AWOS') and c.iemid = s.iemid
        """ % (ts.year, ts.strftime("%Y-%m-%d")))

    if cursor.rowcount > 4:
        res = generic_gridder(cursor, 'highdata')
        nc.variables['high_tmpk'][offset] = datatypes.temperature(
                                                res, 'F').value('K')
        cursor.scroll(0, mode='absolute')
        res = generic_gridder(cursor, 'lowdata')
        nc.variables['low_tmpk'][offset] = datatypes.temperature(
                                            res, 'F').value('K')
        cursor.scroll(0, mode='absolute')
    else:
        print "%s has %02i entries, FAIL" % (ts.strftime("%Y-%m-%d"),
                                             cursor.rowcount)


def main(ts, irealtime):
    # Load up our netcdf file!
    nc = netCDF4.Dataset("/mesonet/data/iemre/%s_mw_daily.nc" % (ts.year,),
                         'a')
    # For this date, the 12 UTC COOP obs will match the date
    grid_day12(nc, ts)
    do_precip12(nc, ts)
    nc.close()
    # This is actually yesterday!
    if irealtime:
        ts -= datetime.timedelta(days=1)
    nc = netCDF4.Dataset("/mesonet/data/iemre/%s_mw_daily.nc" % (ts.year,),
                         'a')
    grid_day(nc, ts)
    do_precip(nc, ts)
    nc.close()

if __name__ == "__main__":
    if len(sys.argv) == 4:
        ts = datetime.date(int(sys.argv[1]), int(sys.argv[2]),
                           int(sys.argv[3]))
        main(ts, False)
    else:
        ts = datetime.date.today()
        main(ts, True)
