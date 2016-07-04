import netCDF4
from pyiem import iemre
from pyiem.plot import MapPlot, nwsprecip
import matplotlib.pyplot as plt
import datetime
import numpy as np

nc = netCDF4.Dataset("/mesonet/data/iemre/2016_mw_mrms_daily.nc", 'r')
idx = iemre.daily_offset(datetime.date(2016, 7, 3))
grid = np.zeros((len(nc.dimensions['lat']),
                 len(nc.dimensions['lon'])))
total = np.zeros((len(nc.dimensions['lat']),
                  len(nc.dimensions['lon'])))
for i, x in enumerate(range(idx, idx-60, -1)):
    total += nc.variables['p01d'][x, :, :]
    grid = np.where(np.logical_and(grid == 0,
                                   total > 25.4), i, grid)

m = MapPlot(sector='iowa', title='NOAA MRMS Q3: Number of Recent Days till Accumulating 1" of Precip',
  subtitle='valid 4 July 2016: based on per calendar day estimated preciptation, GaugeCorr and RadarOnly products')
lon = np.append(nc.variables['lon'][:], [-80.5])
print lon
lat = np.append(nc.variables['lat'][:], [49.])
print lat
x, y = np.meshgrid(lon, lat)
cmap = nwsprecip()
m.pcolormesh(x, y, grid,
             np.arange(0, 53, 7), cmap=cmap, units='days')
m.drawcounties()
m.drawcities()
m.postprocess(filename='test.png')
m.close()
nc.close()
