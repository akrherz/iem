import sys
import netCDF4
import numpy
import datetime
import psycopg2
from pyiem import iemre, datatypes
import Ngl
import random
import network

nt = network.Table(['IACLIMATE','MNCLIMATE','NDCLIMATE',
         'SDCLIMATE','NECLIMATE','KSCLIMATE','MOCLIMATE','ILCLIMATE',
         'WICLIMATE','MICLIMATE','INCLIMATE','OHCLIMATE','KYCLIMATE'])

COOP = psycopg2.connect(database='coop', user='nobody', host='iemdb')
cursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)

def generic_gridder(cursor, idx):
    """
    Generic gridding algorithm for easy variables
    """
    lats = []
    lons = []
    vals = []
    for row in cursor:
        if row[idx] is not None and nt.sts.has_key(row['station']):
            lats.append(  nt.sts[row['station']]['lat'] ) 
            lons.append(  nt.sts[row['station']]['lon'] )
            vals.append( row[idx]  )
    if len(vals) < 4:
        print "Only %s observations found for %s, won't grid" % (len(vals),
               idx)
        return None
    grid = Ngl.natgrid(lons, lats, vals, iemre.XAXIS, iemre.YAXIS)
    print cursor.rowcount, idx, numpy.max(grid), numpy.min(grid)
    if grid is not None:
        return grid.transpose()
    else:
        return None


def grid_day(nc, ts):
    """
    I proctor the gridding of data on an hourly basis
    @param ts Timestamp of the analysis, we'll consider a 20 minute window
    """
    offset = iemre.daily_offset(ts)
    if ts.day == 29 and ts.month == 2:
        ts = datetime.datetime(2000,3,1)

    sql = """SELECT * from ncdc_climate71 WHERE valid = '%s' and
             substr(station,3,4) != '0000' and substr(station,3,1) != 'C'""" % (
         ts.strftime("%Y-%m-%d"), )
    cursor.execute( sql )
    if cursor.rowcount > 4:
        res = generic_gridder(cursor, 'high')
        if res is not None:
            nc.variables['high_tmpk'][offset] = datatypes.temperature(res, 'F').value('K')
        cursor.scroll(0, mode='absolute')
        res = generic_gridder(cursor, 'low')
        if res is not None:
            nc.variables['low_tmpk'][offset] = datatypes.temperature(res, 'F').value('K')
        cursor.scroll(0, mode='absolute')
        res = generic_gridder(cursor, 'precip')
        if res is not None:
            nc.variables['p01d'][offset] = res * 25.4
    else:
        print "%s has %02i entries, FAIL" % (ts.strftime("%Y-%m-%d"), 
            cursor.rowcount)

def main(ts):
    # Load up a station table we are interested in

    # Load up our netcdf file!
    nc = netCDF4.Dataset("/mesonet/data/iemre/mw_dailyc.nc", 'a')
    grid_day(nc , ts)

    nc.close()

if __name__ == "__main__":
    if len(sys.argv) == 4:
        ts = datetime.datetime( int(sys.argv[1]),int(sys.argv[2]),
                           int(sys.argv[3]) )
        main(ts)
    else:
        sts = datetime.datetime(2000,1,1)
        ets = datetime.datetime(2001,1,1)
        interval = datetime.timedelta(days=1)
        now = sts
        while now < ets:
            print now
            main( now )
            now += interval
