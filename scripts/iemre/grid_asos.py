import sys
import netCDF3
import numpy
import mx.DateTime
from pyIEM import iemdb, mesonet
import Ngl
import constants

i = iemdb.iemdb()
mesosite = i['mesosite']
asos = i['asos']
iem = i['iem']
locs = {}

def load_stationtable():
    sql = """SELECT id, x(geom) as lon, y(geom) as lat from
         stations where network IN ('IA_ASOS','MO_ASOS','IL_ASOS',
         'WI_ASOS','MN_ASOS', 'SD_ASOS', 'NE_ASOS', 'KS_ASOS', 'AWOS')"""
    rs = mesosite.query( sql ).dictresult()
    for i in range(len(rs)):
        locs[ rs[i]['id'] ] = rs[i]
    ids = `locs.keys()`
    ids = "(%s)" % (ids[1:-1],)

def grid_skyc(rs):
    lats = []
    lons = []
    vals = []
    for i in range(len(rs)):
        v =  max(rs[i]['max_skyc1'], rs[i]['max_skyc2'], rs[i]['max_skyc3'])
        if v is not None:
            lats.append(  locs[rs[i]['station']]['lat'] )
            lons.append(  locs[rs[i]['station']]['lon'] )
            vals.append( float(v) )
    if len(vals) < 4:
        print "No SKYC data at all for time: %s" % (ts,)   
        return None
    grid = Ngl.natgrid(lons, lats, vals, constants.XAXIS, constants.YAXIS)
    if grid is not None:
        gt = grid.transpose()
        gt = numpy.where(gt > 0., gt, 0.0)
        return numpy.where(gt > 100., 100., gt)
    else:
        return None

def generic_gridder(rs, idx):
    """
    Generic gridding algorithm for easy variables
    """
    lats = []
    lons = []
    vals = []
    for i in range(len(rs)):
        if rs[i][idx] is not None:
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


def grid_hour(nc, ts):
    """
    I proctor the gridding of data on an hourly basis
    @param ts Timestamp of the analysis, we'll consider a 20 minute window
    """
    ids = `locs.keys()`
    ids = "(%s)" % (ids[1:-1],)
    ts0 = ts - mx.DateTime.RelativeDateTime(minutes=10)
    ts1 = ts + mx.DateTime.RelativeDateTime(minutes=10)

    offset = int((ts - (ts + mx.DateTime.RelativeDateTime(month=1,day=1,hour=1))).hours)

    # If we are near realtime, look in IEMAccess instead of ASOS database
    if (mx.DateTime.gmt() - ts).hours < 36:
        dbconn = iem
        table = "current_log"
        pcolumn = "(phour * 25.4)"
    else:
        dbconn = asos
        table = "t%s" % (ts.localtime().year,)
        pcolumn = "p01m"

    sql = """SELECT station,
         max(case when tmpf > -60 and tmpf < 130 THEN tmpf else null end) as max_tmpf,
         max(case when sknt > 0 and sknt < 100 then sknt else 0 end) as max_sknt,
         max(getskyc(skyc1)) as max_skyc1,
         max(getskyc(skyc2)) as max_skyc2,
         max(getskyc(skyc3)) as max_skyc3,
         max(case when %s > 0 and %s < 1000 then %s else 0 end) as max_p01m,
         max(case when dwpf > -60 and dwpf < 100 THEN dwpf else null end) as max_dwpf from %s  
         WHERE station in %s and 
         valid >= '%s+00' and valid < '%s+00' GROUP by station""" % (
         pcolumn, pcolumn, pcolumn, table, ids, 
         ts0.strftime("%Y-%m-%d %H:%M"), ts1.strftime("%Y-%m-%d %H:%M") )
    rs = dbconn.query( sql ).dictresult()
    if len(rs) > 4:
        res = generic_gridder(rs, 'max_tmpf')
        if res is not None:
            nc.variables['tmpk'][offset] = constants.f2k(res)
        res = grid_skyc(rs)
        if res is not None:
            nc.variables['skyc'][offset] = res
    else:
        print "%s has %02i entries, FAIL" % (ts.strftime("%Y-%m-%d %H:%M"), 
            len(rs))

def main(ts):
    # Load up a station table we are interested in
    load_stationtable()

    # Load up our netcdf file!
    nc = netCDF3.Dataset("/mnt/mesonet/data/iemre/%s_hourly.nc" % (ts.year,), 'a')
    grid_hour(nc , ts)

    nc.close()

if __name__ == "__main__":
    if len(sys.argv) == 5:
        ts = mx.DateTime.DateTime( int(sys.argv[1]),int(sys.argv[2]),
                           int(sys.argv[3]), int(sys.argv[4]) )
    else:
        ts = mx.DateTime.gmt() + mx.DateTime.RelativeDateTime(minute=0,second=0)
    main(ts)
