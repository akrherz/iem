# Grid hourly ASOS data please
# Temperature (K),
# Wind speed (mps),
# % Sun shine, 
# Precipitation, 
# Relative humidity.

import sys
import netCDF3
import numpy
import mx.DateTime
from pyIEM import iemdb, mesonet
import Ngl
i = iemdb.iemdb()
mesosite = i['mesosite']
asos = i['asos']
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
        print "No TMPF data at all for time: %s" % (ts,)   
        return None
    grid = Ngl.natgrid(lons, lats, vals, constants.XAXIS, constants.YAXIS)
    if grid is not None:
        return grid.transpose()
    else:
        return None


def grid_hour(nc, ts):
    ids = `locs.keys()`
    ids = "(%s)" % (ids[1:-1],)
    sql = """SELECT station,
         max(case when tmpf > -60 and tmpf < 130 THEN tmpf else null end) as max_tmpf,
         max(case when sknt > 0 and sknt < 100 then sknt else 0 end) as max_sknt,
         max(getskyc(skyc1)) as max_skyc1,
         max(getskyc(skyc2)) as max_skyc2,
         max(getskyc(skyc3)) as max_skyc3,
         max(case when p01m > 0 and p01m < 1000 then p01m else 0 end) as max_p01m,
         max(case when dwpf > -60 and dwpf < 100 THEN dwpf else null end) as max_dwpf from t%s  
         WHERE station in %s and 
         valid >= '%s' and valid < '%s' GROUP by station""" % (
         ts.gmtime().year, ids, 
         ts.strftime("%Y-%m-%d %H:%M"),
     (ts + mx.DateTime.RelativeDateTime(hours=1)).strftime("%Y-%m-%d %H:%M") )
    rs = asos.query( sql ).dictresult()
    if len(rs) > 4:
        grid_tmpf(nc, ts, rs)
        grid_relh(nc, ts, rs)
        grid_wind(nc, ts, rs)
        grid_skyc(nc, ts, rs)
        grid_p01m(nc, ts, rs)
    else:
        print "%s has %02i entries, FAIL" % (ts.strftime("%Y-%m-%d %H:%M"), 
            len(rs))

#
#create_netcdf()
#sys.exit()
load_stationtable()
nc = netCDF3.Dataset("data/asosgrid.nc", 'a')
now = sts
#now = mx.DateTime.DateTime(1980,1,1)
while now < ets:
  #print now
  #if now not in badtimes:
  grid_hour(nc , now)
  now += mx.DateTime.RelativeDateTime(hours=1)

nc.close()
