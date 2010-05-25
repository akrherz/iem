import sys
import netCDF3
import numpy
import mx.DateTime
from pyIEM import iemdb, mesonet
import Ngl
import constants

i = iemdb.iemdb()
mesosite = i['mesosite']
coop = i['coop']
locs = {}

def load_stationtable():
    sql = """SELECT id, x(geom) as lon, y(geom) as lat from
         stations where network IN ('IACLIMATE')"""
    rs = mesosite.query( sql ).dictresult()
    for i in range(len(rs)):
        locs[ rs[i]['id'].lower() ] = rs[i]

def generic_gridder(rs, idx):
    """
    Generic gridding algorithm for easy variables
    """
    lats = []
    lons = []
    vals = []
    for i in range(len(rs)):
        if rs[i][idx] is not None and locs.has_key(rs[i]['station']):
            lats.append(  locs[rs[i]['station']]['lat'] )
            lons.append(  locs[rs[i]['station']]['lon'] )
            vals.append( rs[i][idx]  )
    if len(vals) < 4:
        print "Only %s observations found for %s, won't grid" % (len(vals),
               idx)
        return None
    grid = Ngl.natgrid(lons, lats, vals, constants.XAXIS, constants.YAXIS)
    if grid is not None:
        return grid.transpose()
    else:
        return None


def grid_day(nc, ts):
    """
    I proctor the gridding of data on an hourly basis
    @param ts Timestamp of the analysis, we'll consider a 20 minute window
    """
    offset = int((ts - (ts + mx.DateTime.RelativeDateTime(month=1,day=1,hour=0))).days)


    sql = """SELECT * from climate51 WHERE valid = '%s' and
             station != 'ia0000' """ % (
         ts.strftime("%Y-%m-%d"), )
    rs = coop.query( sql ).dictresult()
    if len(rs) > 4:
        res = generic_gridder(rs, 'high')
        if res is not None:
            nc.variables['high_tmpk'][offset] = constants.f2k(res)
        res = generic_gridder(rs, 'low')
        if res is not None:
            nc.variables['low_tmpk'][offset] = constants.f2k(res)
        res = generic_gridder(rs, 'precip')
        if res is not None:
            nc.variables['p01d'][offset] = res * 24.5
    else:
        print "%s has %02i entries, FAIL" % (ts.strftime("%Y-%m-%d"), 
            len(rs))

def main(ts):
    # Load up a station table we are interested in
    load_stationtable()

    # Load up our netcdf file!
    nc = netCDF3.Dataset("/mnt/mesonet/data/iemre/dailyc.nc", 'a')
    grid_day(nc , ts)

    nc.close()

if __name__ == "__main__":
    if len(sys.argv) == 4:
        ts = mx.DateTime.DateTime( int(sys.argv[1]),int(sys.argv[2]),
                           int(sys.argv[3]) )
        main(ts)
    else:
        sts = mx.DateTime.DateTime(2000,1,1)
        ets = mx.DateTime.DateTime(2001,1,1)
        interval = mx.DateTime.RelativeDateTime(days=1)
        now = sts
        while now < ets:
            print now
            main( now )
            now += interval
