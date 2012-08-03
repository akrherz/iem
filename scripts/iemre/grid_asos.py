import sys
import netCDF4
import numpy
import mx.DateTime
import Ngl
import iemre
import iemdb
import mesonet
import network
import psycopg2.extras

nt = network.Table(('IA_ASOS','MO_ASOS','IL_ASOS',
         'WI_ASOS','MN_ASOS', 'SD_ASOS', 'NE_ASOS', 'KS_ASOS', 'AWOS',
         'IN_ASOS','KY_ASOS','OH_ASOS','MI_ASOS'))

ids = `nt.sts.keys()`
ids = "(%s)" % (ids[1:-1],)

def grid_wind(rs):
    """
    Grid winds based on u and v components
    @param rs array of dicts
    @return uwnd, vwnd
    """
    lats = []
    lons = []
    udata = []
    vdata = []
    for row in rs:
        if row['sknt'] is None or row['drct'] is None:
            continue
        # mps
        u,v = mesonet.uv( row['sknt'] / 0.514, row['drct'] )
        if v is not None:
            lats.append(  nt.sts[row['station']]['lat'] )
            lons.append(  nt.sts[row['station']]['lon'] )
            vdata.append( v )
            udata.append( u )
            
    if len(vdata) < 4:
        print "No wind data at all for time: %s" % (ts,)   
        return None
    
    ugrid = Ngl.natgrid(lons, lats, udata, iemre.XAXIS, iemre.YAXIS)
    vgrid = Ngl.natgrid(lons, lats, vdata, iemre.XAXIS, iemre.YAXIS)
    if ugrid is not None:
        ugt = ugrid.transpose()
        vgt = vgrid.transpose()
        return ugt, vgt
    else:
        return None, None

def grid_skyc(rs):
    lats = []
    lons = []
    vals = []
    for row in rs:
        v =  max(row['max_skyc1'], row['max_skyc2'], row['max_skyc3'])
        if v is not None:
            lats.append(  nt.sts[row['station']]['lat'] )
            lons.append(  nt.sts[row['station']]['lon'] )
            vals.append( float(v) )
    if len(vals) < 4:
        print "No SKYC data at all for time: %s" % (ts,)   
        return None
    grid = Ngl.natgrid(lons, lats, vals, iemre.XAXIS, iemre.YAXIS)
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
    for row in rs:
        if row[idx] is not None:
            lats.append( nt.sts[row['station']]['lat'] )
            lons.append( nt.sts[row['station']]['lon'] )
            vals.append( row[idx]  )
    if len(vals) < 4:
        print "Only %s observations found for %s, won't grid" % (len(vals),
               idx)
        return None
    grid = Ngl.natgrid(lons, lats, vals, iemre.XAXIS, iemre.YAXIS)
    if grid is not None:
        return grid.transpose()
    else:
        return None


def grid_hour(nc, ts):
    """
    I proctor the gridding of data on an hourly basis
    @param ts Timestamp of the analysis, we'll consider a 20 minute window
    """
    ts0 = ts - mx.DateTime.RelativeDateTime(minutes=10)
    ts1 = ts + mx.DateTime.RelativeDateTime(minutes=10)

    offset = int((ts - (ts + mx.DateTime.RelativeDateTime(month=1,day=1,hour=1))).hours)

    # If we are near realtime, look in IEMAccess instead of ASOS database
    if (mx.DateTime.gmt() - ts).hours < 36:
        dbconn = iemdb.connect('iem', bypass=True)
        pcursor = dbconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        table = "current_log"
        pcolumn = "(phour * 25.4)"
        sql = """SELECT t.id as station,
         max(case when tmpf > -60 and tmpf < 130 THEN tmpf else null end) as max_tmpf,
         max(case when sknt > 0 and sknt < 100 then sknt else 0 end) as max_sknt,
         max(getskyc(skyc1)) as max_skyc1,
         max(getskyc(skyc2)) as max_skyc2,
         max(getskyc(skyc3)) as max_skyc3,
         max(case when %s > 0 and %s < 1000 then %s else 0 end) as max_p01m,
         max(case when dwpf > -60 and dwpf < 100 THEN dwpf else null end) as max_dwpf,
         max(case when sknt >= 0 then sknt else 0 end) as sknt, 
         max(case when sknt >= 0 then drct else 0 end) as drct from %s s, stations t
         WHERE t.id in %s and t.iemid = s.iemid and 
         valid >= '%s+00' and valid < '%s+00' GROUP by station""" % (
         pcolumn, pcolumn, pcolumn, table, ids, 
         ts0.strftime("%Y-%m-%d %H:%M"), ts1.strftime("%Y-%m-%d %H:%M") )
    else:
        dbconn = iemdb.connect('asos', bypass=True)
        pcursor = dbconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        table = "t%s" % (ts.localtime().year,)
        pcolumn = "p01i"
        sql = """SELECT station,
         max(case when tmpf > -60 and tmpf < 130 THEN tmpf else null end) as max_tmpf,
         max(case when sknt > 0 and sknt < 100 then sknt else 0 end) as max_sknt,
         max(getskyc(skyc1)) as max_skyc1,
         max(getskyc(skyc2)) as max_skyc2,
         max(getskyc(skyc3)) as max_skyc3,
         max(case when %s > 0 and %s < 1000 then %s else 0 end) as max_p01m,
         max(case when dwpf > -60 and dwpf < 100 THEN dwpf else null end) as max_dwpf,
         max(case when sknt >= 0 then sknt else 0 end) as sknt, 
         max(case when sknt >= 0 then drct else 0 end) as drct from %s  
         WHERE station in %s and 
         valid >= '%s+00' and valid < '%s+00' GROUP by station""" % (
         pcolumn, pcolumn, pcolumn, table, ids, 
         ts0.strftime("%Y-%m-%d %H:%M"), ts1.strftime("%Y-%m-%d %H:%M") )

    pcursor.execute( sql )
    
    if pcursor.rowcount > 4:
        rs = []
        for row in pcursor:
            rs.append( row )
        ures, vres = grid_wind(rs)
        if ures is not None:
            nc.variables['uwnd'][offset] = ures
            nc.variables['vwnd'][offset] = vres
            
        res = generic_gridder(rs, 'max_tmpf')
        if res is not None:
            nc.variables['tmpk'][offset] = iemre.f2k(res)

        res = grid_skyc(rs)
        if res is not None:
            nc.variables['skyc'][offset] = res
    else:
        print "%s has %02i entries, FAIL" % (ts.strftime("%Y-%m-%d %H:%M"), 
            len(rs))

def main(ts):
    # Load up our netcdf file!
    nc = netCDF4.Dataset("/mnt/mesonet/data/iemre/%s_mw_hourly.nc" % (ts.year,), 'a')
    grid_hour(nc , ts)

    nc.close()

if __name__ == "__main__":
    if len(sys.argv) == 5:
        ts = mx.DateTime.DateTime( int(sys.argv[1]),int(sys.argv[2]),
                           int(sys.argv[3]), int(sys.argv[4]) )
    else:
        ts = mx.DateTime.gmt() + mx.DateTime.RelativeDateTime(minute=0,second=0)
    main(ts)
