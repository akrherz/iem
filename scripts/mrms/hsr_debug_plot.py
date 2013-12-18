"""
Debug the plotting of HSR
"""

import matplotlib
matplotlib.use('Agg')
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

import nmq
import mx.DateTime
import netCDF4

fig = plt.figure(num=None, figsize=(10.24,7.68))
ax = plt.axes([0.01,0,0.9,1], axisbg=(0.4471,0.6235,0.8117))
map = Basemap(projection='merc', 
        urcrnrlat=30.5, llcrnrlat=30.4, urcrnrlon=-92.6, llcrnrlon=-92.8, 
        lon_0=-98.7, lat_0=39, lat_1=33, lat_2=45,
             resolution='l', ax=ax)
map.fillcontinents(color='0.7',zorder=0)
map.drawstates()

ncfp = nmq.make_mosaic2d_fp(6, mx.DateTime.DateTime(2012,5,11,18,0))
nc = netCDF4.Dataset(ncfp, 'r')
val = nc.variables["hsr"][:,:] / nc.variables['hsr'].Scale

for y in range(952, 958):
    for x in range(1727,1732):
        lon = nmq.TILES[6][0] + (0.01 * x)
        lat = nmq.TILES[6][1] - (0.01 * y)
        xs, ys = map(lon, lat)
        print lon, lat
        ax.text(xs, ys, '%.0f' % (val[y,x]))
nc.close()

fig.savefig('test.png')