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

ets = datetime.datetime(2013,6,18)

offset2 = iemre.daily_offset(ets)

nc = netCDF4.Dataset("/mesonet/data/iemre/2013_mw_daily.nc", 'r')
p2013 = numpy.sum(nc.variables['p01d'][:offset2,:,:] / 25.4,0)

nc = netCDF4.Dataset("/mesonet/data/iemre/2012_mw_daily.nc", 'r')
p2012 = numpy.sum(nc.variables['p01d'][:,:,:] / 25.4,0)

lons = nc.variables['lon'][:]
lats = nc.variables['lat'][:]
x,y = numpy.meshgrid(lons, lats)

extra = lons[-1] + (lons[-1] - lons[-2])
lons = numpy.concatenate([lons, [extra,]])

extra = lats[-1] + (lats[-1] - lats[-2])
lats = numpy.concatenate([lats, [extra,]])
x,y = numpy.meshgrid(lons, lats)

m = MapPlot(sector='iowa', title='1 Jan - 19 Jun 2013 Precipitation vs all of 2012 [inch]')
clevels = [-12,-8,-4,-2,-1,-0.5,-0.25,0,0.25,0.5,1,2,4,8,12]
m.drawcounties()
m.pcolormesh(x, y, p2013 - p2012, numpy.array(clevels), cmap=cm.get_cmap('RdBu'), units='inch')
m.postprocess(filename='test.svg')
import iemplot
iemplot.makefeature('test')

nc.close()

