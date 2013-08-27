import netCDF4
from pyiem.plot import MapPlot
from pyiem import iemre
import datetime
import numpy as np
import matplotlib.cm as cm

sts = datetime.datetime(2013,8,1)
ets = datetime.datetime(2013,8,26)

idx0 = iemre.daily_offset(sts)
idx1 = iemre.daily_offset(ets)

nc = netCDF4.Dataset("/mesonet/data/iemre/2013_mw_mrms_daily.nc", 'r')

lats = nc.variables['lat'][:]
lons = nc.variables['lon'][:]
p01d = np.sum(nc.variables['p01d'][idx0:idx1,:,:],0) / 24.5
nc.close()


m = MapPlot(sector='iowa', title='MRMS 1 August - 26 August 2013 Total Precipitation',
            subtitle='Data from NOAA MRMS Project')
x,y = np.meshgrid(lons, lats)
m.pcolormesh(x, y, p01d, [0.01,0.1,0.25,0.5,0.75,1,2,3,4,5,6], cmap=cm.get_cmap('RdYlBu'),
             label='inches')
m.drawcounties()
m.postprocess(filename='test.ps')
import iemplot
iemplot.makefeature('test')
