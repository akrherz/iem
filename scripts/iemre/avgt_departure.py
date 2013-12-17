"""
 Precipitation departure from the climatology grid
"""
import netCDF4
import numpy
import datetime
from pyiem.datatypes import temperature
from pyiem import iemre
from pyiem.plot import MapPlot
from mpl_toolkits.basemap import maskoceans
import matplotlib.cm as cm

sts = datetime.datetime(2013,12,1)
ets = datetime.datetime(2013,12,16)

offset1 = iemre.daily_offset(sts)
offset2 = iemre.daily_offset(ets)

nc = netCDF4.Dataset("/mesonet/data/iemre/%s_mw_daily.nc" % (sts.year,), 'r')
htk = nc.variables['high_tmpk']
ltk = nc.variables['low_tmpk']

ncc = netCDF4.Dataset("/mesonet/data/iemre/mw_dailyc.nc", 'r')
chtk = ncc.variables['high_tmpk']
cltk = ncc.variables['low_tmpk']

h1 = (numpy.average(htk[offset1:offset2,:,:],0) + numpy.average(htk[offset1:offset2,:,:],0))/2.
h2 = (numpy.average(chtk[offset1:offset2,:,:],0) + numpy.average(chtk[offset1:offset2,:,:],0))/2.
diff = temperature(h1, 'K').value('F') -  temperature(h2, 'K').value('F')

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
            title='1 - 16 Dec 2013 Average Temperature Departure from Average',
            subtitle='2013 vs 1950-2012 Climatology')
m.pcolormesh(x, y, diff, numpy.arange(-12.,13.0,2.), cmap=cm.get_cmap('RdYlBu_r'), units='%')
m.drawcounties()
m.postprocess(filename='test.ps')
import iemplot
iemplot.makefeature('test')

nc.close()
ncc.close()

