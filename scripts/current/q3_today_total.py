"""
 Create a plot of today's estimated precipitation based on the Q3 data
"""
import datetime
import numpy as np
import sys
import pyiem.iemre as iemre
from pyiem.datatypes import distance
import netCDF4
import pytz
import matplotlib
matplotlib.use('agg')
from pyiem.plot import MapPlot, nwsprecip  # NOPEP8


def doday(ts, realtime):
    """
    Create a plot of precipitation stage4 estimates for some day
    """
    lts = datetime.datetime.utcnow().replace(
                tzinfo=pytz.timezone("UTC"))
    lts = lts.astimezone(pytz.timezone("America/Chicago"))
    # make assumptions about the last valid MRMS data
    if realtime:
        # Up until :59 after of the last hour
        lts = (lts - datetime.timedelta(hours=1)).replace(minute=59)
    else:
        lts = lts.replace(year=ts.year, month=ts.month, day=ts.day,
                          hour=23, minute=59)

    idx = iemre.daily_offset(ts)
    ncfn = "/mesonet/data/iemre/%s_mw_mrms_daily.nc" % (ts.year,)
    nc = netCDF4.Dataset(ncfn)
    precip = nc.variables['p01d'][idx, :, :]
    lats = nc.variables['lat'][:]
    lons = nc.variables['lon'][:]
    subtitle = "Total between 12:00 AM and %s" % (
                                            lts.strftime("%I:%M %p %Z"),)
    routes = 'ac'
    if not realtime:
        routes = 'a'

    # clevs = np.arange(0, 0.25, 0.05)
    # clevs = np.append(clevs, np.arange(0.25, 3., 0.25))
    # clevs = np.append(clevs, np.arange(3., 10.0, 1))
    clevs = [0.01, 0.1, 0.25, 0.5, 0.75, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8,
             10]

    sector = 'iowa'
    pqstr = ("plot %s %s00 %s_q2_1d.png %s_q2_1d.png png"
             ) % (routes, ts.strftime("%Y%m%d%H"), sector, sector)
    m = MapPlot(title=("%s NCEP MRMS Q3 Today's Precipitation"
                       ) % (ts.strftime("%-d %b %Y"),),
                subtitle=subtitle, sector=sector)

    (x, y) = np.meshgrid(lons, lats)

    m.pcolormesh(x, y, distance(precip, 'MM').value('IN'), clevs,
                 cmap=nwsprecip(), units='inch')
    m.drawcounties()
    m.postprocess(pqstr=pqstr, view=False)
    m.close()


def main():
    if len(sys.argv) == 4:
        date = datetime.date(int(sys.argv[1]), int(sys.argv[2]),
                             int(sys.argv[3]))
        realtime = False
    else:
        date = datetime.date.today()
        realtime = True
    doday(date, realtime)


if __name__ == "__main__":
    main()
