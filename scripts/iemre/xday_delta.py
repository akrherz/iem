"""
 Precipitation departure from the climatology grid
"""
import netCDF4
import numpy as np
import datetime
from pyiem import iemre
from pyiem.plot import MapPlot
from mpl_toolkits.basemap import maskoceans
import matplotlib.cm as cm

sts = datetime.datetime(2013,5,1)
ets = datetime.datetime(2013,10,1)

offset1 = iemre.daily_offset(sts)
offset2 = iemre.daily_offset(ets)

nc = netCDF4.Dataset("/mesonet/data/iemre/%s_mw_daily.nc" % (sts.year,), 'r')
p01d = nc.variables['p01d']

ncc = netCDF4.Dataset("/mesonet/data/iemre/mw_dailyc.nc", 'r')
cp01d = ncc.variables['p01d']

lons = nc.variables['lon'][:]
lats = nc.variables['lat'][:]

days = np.zeros( (len(lats), len(lons)), 'f')

for i in range(offset1,offset2):
    climo = np.sum(cp01d[i-30:i,:,:],0)
    obs = np.sum(p01d[i-30:i,:,:],0)

    days += np.where(obs < (climo * 0.33), 1, 0)
    print i, np.max(days)

x,y = np.meshgrid(lons, lats)
#days = maskoceans(x, y, days)
extra = lons[-1] + (lons[-1] - lons[-2])
lons = np.concatenate([lons, [extra,]])

extra = lats[-1] + (lats[-1] - lats[-2])
lats = np.concatenate([lats, [extra,]])
x,y = np.meshgrid(lons, lats)

m = MapPlot(sector='midwest',
            title='1 May - 1 Oct Days with Past 30 Days Precip < 33% of Average',
            subtitle='2013 vs 1950-2012 Climatology')
cmap=cm.get_cmap('RdYlBu_r')
cmap.set_under('white')
cmap.set_over('black')
m.pcolormesh(x, y, days, np.array([1,2,5,7,10,15,20,25,30,35,40,45,50,60]), 
             cmap=cmap, units='days')
#m.drawcounties()
m.postprocess(filename='test.ps')
import iemplot
iemplot.makefeature('test')

nc.close()
ncc.close()

