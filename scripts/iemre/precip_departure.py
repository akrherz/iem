"""
 Precipitation departure from the climatology grid
"""
import netCDF4
import numpy
import datetime
from pyiem import iemre
from pyiem.plot import MapPlot
from mpl_toolkits.basemap import maskoceans

sts = datetime.datetime(2013,5,1)
ets = datetime.datetime(2013,6,10)

offset1 = iemre.daily_offset(sts)
offset2 = iemre.daily_offset(ets)

nc = netCDF4.Dataset("/mesonet/data/iemre/%s_mw_daily.nc" % (sts.year,), 'r')
p01d = nc.variables['p01d']

ncc = netCDF4.Dataset("/mesonet/data/iemre/mw_dailyc.nc", 'r')
cp01d = ncc.variables['p01d']
for i in range(offset1,offset2):
    if cp01d[i,5,5] > 20:
        print i, p01d[i,5,5], cp01d[i,5,5]

diff = (numpy.sum(p01d[offset1:offset2,:,:],0) -  numpy.sum(cp01d[offset1:offset2,:,:],0)) / 25.4
print numpy.sum(p01d[offset1:offset2,5,5]), numpy.sum(cp01d[offset1:offset2,5,5])
print numpy.max(diff), numpy.min(diff)

lons = nc.variables['lon'][:]
lats = nc.variables['lat'][:]
x,y = numpy.meshgrid(lons, lats)
diff = maskoceans(x, y, diff)
extra = lons[-1] + (lons[-1] - lons[-2])
lons = numpy.concatenate([lons, [extra,]])

extra = lats[-1] + (lats[-1] - lats[-2])
lats = numpy.concatenate([lats, [extra,]])
x,y = numpy.meshgrid(lons, lats)

m = MapPlot(sector='midwest')
m.pcolormesh(x, y, diff, numpy.arange(-8,8.1,1))
m.postprocess(view=True)

nc.close()
ncc.close()

