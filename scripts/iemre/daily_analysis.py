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

COOP = psycopg2.connect(database='iem', host='iemdb', user='nobody')
icursor = COOP.cursor(cursor_factory=DictCursor)


def generic_gridder(rs, idx):
    """
    Generic gridding algorithm for easy variables
    """
    lats = []
    lons = []
    vals = []
    for row in rs:
        if row[idx] is not None:
            lats.append(  row['lat']  )
            lons.append(  row['lon'] )
            vals.append( row[idx]  )
    if len(vals) < 4:
        print "Only %s observations found for %s, won't grid" % (len(vals),
               idx)
        return None
    
    nn = NearestNDInterpolator((np.array(lons), np.array(lats)), np.array(vals))
    xi, yi = np.meshgrid(iemre.XAXIS, iemre.YAXIS)
    grid = nn(xi, yi)
    
    return grid


def do_precip(nc, ts):
    """Compute the precip totals based on the hourly analysis totals"""
    offset = iemre.daily_offset(ts)
    ets = ts.replace(hour=12, tzinfo=pytz.timezone("UTC"))
    sts = ets - datetime.timedelta(hours=24)
    offset1 = iemre.hourly_offset(sts)
    offset2 = iemre.hourly_offset(ets)
    hnc = netCDF4.Dataset("/mesonet/data/iemre/%s_mw_hourly.nc" % (ts.year,))
    phour = np.sum(hnc.variables['p01m'][offset1:offset2, :, :], 0)
    nc.variables['p01d'][offset] = phour
    hnc.close()


def grid_day(nc, ts):
    """
    """
    offset = iemre.daily_offset(ts)
    icursor.execute("""
       SELECT ST_x(s.geom) as lon, ST_y(s.geom) as lat, 
       (CASE WHEN pday >= 0 then pday else null end) as precipdata,
       (CASE WHEN max_tmpf > -50 and max_tmpf < 130 then max_tmpf else null end) as highdata,
       (CASE WHEN min_tmpf > -50 and min_tmpf < 95 then min_tmpf else null end) as lowdata 
       from summary_%s c, stations s WHERE day = '%s' and 
       s.network in ('IA_ASOS', 'MN_ASOS', 'WI_ASOS', 'IL_ASOS', 'MO_ASOS',
        'KS_ASOS', 'NE_ASOS', 'SD_ASOS', 'ND_ASOS', 'KY_ASOS', 'MI_ASOS',
        'OH_ASOS', 'AWOS') and c.iemid = s.iemid
        """ % (ts.year, ts.strftime("%Y-%m-%d")))

    if icursor.rowcount > 4:
        res = generic_gridder(icursor, 'highdata')
        nc.variables['high_tmpk'][offset] = datatypes.temperature(res, 'F').value('K')
        icursor.scroll(0, mode='absolute')
        res = generic_gridder(icursor, 'lowdata')
        nc.variables['low_tmpk'][offset] = datatypes.temperature(res, 'F').value('K')
        icursor.scroll(0, mode='absolute')
        #res = generic_gridder(icursor, 'precipdata')
        #nc.variables['p01d'][offset] = res * 25.4
    else:
        print "%s has %02i entries, FAIL" % (ts.strftime("%Y-%m-%d"), 
            icursor.rowcount)


def main(ts):
    # Load up our netcdf file!
    nc = netCDF4.Dataset("/mesonet/data/iemre/%s_mw_daily.nc" % (ts.year,),
                         'a')
    grid_day(nc, ts)
    do_precip(nc, ts)
    nc.close()

if __name__ == "__main__":
    if len(sys.argv) == 4:
        ts = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]),
                               int(sys.argv[3]))
    else:
        ts = datetime.datetime.now()
        ts = ts.replace(hour=0, minute=0, second=0)
    main(ts)
