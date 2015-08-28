'''
  I produce the hourly analysis used by IEMRE
'''

import sys
import netCDF4
import numpy as np
import datetime
from pyiem import iemre
from pyiem import meteorology
import pyiem.datatypes as dt
from pyiem.network import Table as NetworkTable
import psycopg2.extras
import pytz
from scipy.interpolate import NearestNDInterpolator

nt = NetworkTable(('IA_ASOS', 'MO_ASOS', 'IL_ASOS', 'ND_ASOS',
                   'WI_ASOS', 'MN_ASOS', 'SD_ASOS', 'NE_ASOS', 'KS_ASOS',
                   'AWOS', 'IN_ASOS', 'KY_ASOS', 'OH_ASOS', 'MI_ASOS'))

ids = repr(nt.sts.keys())
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
        (u, v) = meteorology.uv(dt.speed(row['sknt'], 'KT'),
                                dt.direction(row['drct'], 'DEG'))
        if v is not None:
            lats.append(nt.sts[row['station']]['lat'])
            lons.append(nt.sts[row['station']]['lon'])
            vdata.append(v.value("MPS"))
            udata.append(u.value("MPS"))

    if len(vdata) < 4:
        print "No wind data at all"
        return None

    xi, yi = np.meshgrid(iemre.XAXIS, iemre.YAXIS)
    nn = NearestNDInterpolator((lons, lats), np.array(udata))
    ugrid = nn(xi, yi)
    nn = NearestNDInterpolator((lons, lats), np.array(vdata))
    vgrid = nn(xi, yi)
    if ugrid is not None:
        ugt = ugrid
        vgt = vgrid
        return ugt, vgt
    else:
        return None, None


def grid_skyc(rs):
    lats = []
    lons = []
    vals = []
    for row in rs:
        v = max(row['max_skyc1'], row['max_skyc2'], row['max_skyc3'])
        if v is not None:
            lats.append(nt.sts[row['station']]['lat'])
            lons.append(nt.sts[row['station']]['lon'])
            vals.append(float(v))
    if len(vals) < 4:
        print "No SKYC data at all"
        return None
    xi, yi = np.meshgrid(iemre.XAXIS, iemre.YAXIS)
    nn = NearestNDInterpolator((lons, lats), np.array(vals))
    grid = nn(xi, yi)
    if grid is not None:
        gt = grid
        gt = np.where(gt > 0., gt, 0.0)
        return np.where(gt > 100., 100., gt)
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
            lats.append(nt.sts[row['station']]['lat'])
            lons.append(nt.sts[row['station']]['lon'])
            vals.append(row[idx])
    if len(vals) < 4:
        print "Only %s observations found for %s, won't grid" % (len(vals),
                                                                 idx)
        return None
    xi, yi = np.meshgrid(iemre.XAXIS, iemre.YAXIS)
    nn = NearestNDInterpolator((lons, lats), np.array(vals))
    grid = nn(xi, yi)
    if grid is not None:
        return grid
    else:
        return None


def grid_hour(nc, ts):
    """
    I proctor the gridding of data on an hourly basis
    @param ts Timestamp of the analysis, we'll consider a 20 minute window
    """
    ts0 = ts - datetime.timedelta(minutes=10)
    ts1 = ts + datetime.timedelta(minutes=10)
    offset = iemre.hourly_offset(ts)
    utcnow = datetime.datetime.utcnow()
    utcnow = (utcnow.replace(tzinfo=pytz.timezone("UTC")) -
              datetime.timedelta(hours=36))

    # If we are near realtime, look in IEMAccess instead of ASOS database
    if utcnow < ts:
        dbconn = psycopg2.connect(database='iem', host='iemdb', user='nobody')
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
 valid >= '%s' and valid < '%s' GROUP by station
         """ % (pcolumn, pcolumn, pcolumn, table, ids, ts0, ts1)
    else:
        dbconn = psycopg2.connect(database='asos', host='iemdb', user='nobody')
        pcursor = dbconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        table = "t%s" % (ts.year,)
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
 valid >= '%s' and valid < '%s' GROUP by station
         """ % (pcolumn, pcolumn, pcolumn, table, ids, ts0, ts1)

    pcursor.execute(sql)

    if pcursor.rowcount > 4:
        rs = []
        for row in pcursor:
            rs.append(row)
        ures, vres = grid_wind(rs)
        if ures is not None:
            nc.variables['uwnd'][offset] = ures
            nc.variables['vwnd'][offset] = vres

        res = generic_gridder(rs, 'max_tmpf')
        if res is not None:
            nc.variables['tmpk'][offset] = dt.temperature(res, 'F').value('K')

        res = grid_skyc(rs)
        if res is not None:
            nc.variables['skyc'][offset] = res
    else:
        print "%s has %02i entries, FAIL" % (ts.strftime("%Y-%m-%d %H:%M"),
                                             pcursor.rowcount)


def main():
    """Go Main"""
    if len(sys.argv) == 5:
        ts = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]),
                               int(sys.argv[3]), int(sys.argv[4]))
    else:
        ts = datetime.datetime.utcnow()
        ts = ts.replace(second=0, minute=0)
    ts = ts.replace(tzinfo=pytz.timezone("UTC"))
    # Load up our netcdf file!
    nc = netCDF4.Dataset("/mesonet/data/iemre/%s_mw_hourly.nc" % (ts.year,),
                         'a')
    grid_hour(nc, ts)

    nc.close()

if __name__ == "__main__":
    main()
