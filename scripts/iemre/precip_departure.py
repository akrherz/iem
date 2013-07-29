"""
 Precipitation departure from the climatology grid
"""
import netCDF4
import numpy
import datetime
from pyiem import iemre
from pyiem.plot import MapPlot
from mpl_toolkits.basemap import maskoceans
import matplotlib.cm as cm

sts = datetime.datetime(2013,6,1)
ets = datetime.datetime(2013,7,9)

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
#lons = numpy.concatenate([lons, [extra,]])

extra = lats[-1] + (lats[-1] - lats[-2])
#lats = numpy.concatenate([lats, [extra,]])
x,y = numpy.meshgrid(lons, lats)

m = MapPlot(sector='iowa',
            title='1 June - 9 July 2013 Precipitation Departure',
            subtitle='2013 vs 1950-2012 Climatology')
m.contourf(x, y, diff, numpy.arange(-5.,5.1,1.), cmap=cm.get_cmap('RdYlBu'))
m.drawcounties()
m.postprocess(filename='test.ps')
import iemplot
iemplot.makefeature('test')

nc.close()
ncc.close()

