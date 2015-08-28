import netCDF4
from pyiem import iemre, plot
import numpy
import datetime
import pytz

sts = datetime.datetime(2015,5,1, 0)
sts = sts.replace(tzinfo=pytz.timezone("UTC"))
ets = datetime.datetime(2015,6,28, 0)
ets = ets.replace(tzinfo=pytz.timezone("UTC"))


nc = netCDF4.Dataset('/mesonet/data/iemre/2015_mw_hourly.nc')
lons = nc.variables['lon'][:]
lats = nc.variables['lat'][:]
running = numpy.zeros( (len(nc.dimensions['lat']), len(nc.dimensions['lon'])))
maxval = numpy.zeros( (len(nc.dimensions['lat']), len(nc.dimensions['lon'])))
interval = datetime.timedelta(hours=1)
now = sts
i,j = iemre.find_ij(-93.61, 41.99)
while now < ets:
    offset = iemre.hourly_offset(now)
    p01m = nc.variables['p01m'][offset]
    # 0.05in is 1.27 mm
    this = numpy.where(p01m > 1.27, 1, 0)
    running = numpy.where(this == 1, 0, running + 1)
    maxval = numpy.where(running > maxval, running, maxval)
    print now, running[j,i], maxval[j,i]
    
    now += interval

nc2 = netCDF4.Dataset("/mesonet/data/iemre/state_weights.nc")
domain = nc2.variables['domain'][:]
nc2.close()
#maxval = numpy.where(domain == 1, maxval, 1.e20)

m = plot.MapPlot(sector='midwest',
                title='1 May - 28 June 2015 Max Period between hourly 0.05+ inch Precip',
                subtitle='based on NCEP Stage IV data')

extra = lons[-1] + (lons[-1] - lons[-2])
#lons = numpy.concatenate([lons, [extra,]])

extra = lats[-1] + (lats[-1] - lats[-2])
lats[-1] = extra
#lats = numpy.concatenate([lats, [extra,]])

x, y = numpy.meshgrid(lons, lats)
#m.pcolormesh(x, y, maxval / 24.0, numpy.arange(0,25,1), units='days')
m.contourf(x, y, maxval / 24.0, numpy.arange(0,25,2), units='days')
m.postprocess(filename='test.png')
