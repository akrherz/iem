import netCDF4
from pyiem.datatypes import distance
import matplotlib
matplotlib.use('agg')
from pyiem.plot import MapPlot
from pyiem import iemre
import datetime
import numpy as np
import sys


def do_month(year, month, routes):
    """ Generate a MRMS plot for the month!"""

    sts = datetime.datetime(year,month,1)
    ets = sts + datetime.timedelta(days=35)
    ets = ets.replace(day=1)

    today = datetime.datetime.now()
    if ets > today:
        ets = today

    idx0 = iemre.daily_offset(sts)
    idx1 = iemre.daily_offset(ets)

    nc = netCDF4.Dataset("/mesonet/data/iemre/%s_mw_mrms_daily.nc" % (year,),
                          'r')

    lats = nc.variables['lat'][:]
    lons = nc.variables['lon'][:]
    p01d = distance(np.sum(nc.variables['p01d'][idx0:idx1,:,:],0),
                    'MM').value('IN')
    nc.close()

    m = MapPlot(sector='iowa', title='MRMS %s - %s Total Precipitation' % (
            sts.strftime("%-d %b"), 
            (ets - datetime.timedelta(days=1)).strftime("%-d %b %Y")),
            subtitle='Data from NOAA MRMS Project')
    x,y = np.meshgrid(lons, lats)
    bins = [0.01, 0.1, 0.5, 1, 1.5, 2, 3, 4, 5, 6, 7, 8, 12, 16, 20]
    m.pcolormesh(x, y, p01d, bins, units='inches')
    m.drawcounties()
    currentfn = "summary/iowa_mrms_q3_month.png"
    archivefn = sts.strftime("%Y/%m/summary/iowa_mrms_q3_month.png")
    pqstr = "plot %s %s00 %s %s png" % (
                routes, sts.strftime("%Y%m%d%H"), currentfn, archivefn)
    m.postprocess(pqstr=pqstr)


def main():
    #
    if len(sys.argv) == 3:
        do_month(int(sys.argv[1]), int(sys.argv[2]), 'm')
    else:
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        do_month(yesterday.year, yesterday.month, 'cm')

if __name__ == '__main__':
    main()
