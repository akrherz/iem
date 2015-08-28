# coding: utf-8
import netCDF4
import matplotlib.pyplot as plt
import numpy as np
from pyiem.plot import maue
import matplotlib.cm as cm

data = np.zeros((281, 94), 'f')

nc = netCDF4.Dataset('/mesonet/data/iemre/2013_mw_daily.nc', 'r')
lons = nc.variables['lon'][:]
clnc = netCDF4.Dataset('/mesonet/data/iemre/mw_dailyc.nc', 'r')

p01d = nc.variables['high_tmpk']
cltmpk = clnc.variables['high_tmpk']

for i in range(281):
    data[i,:] = np.average(p01d[i,:,:] - cltmpk[i,:,:], 0)
    #data[i,:] = np.average(p01d[i,:,:], 0)

(fig, ax) = plt.subplots(1,1)

res = ax.imshow( data[:,:] , cmap=cm.get_cmap('RdYlBu_r'), aspect='auto',
                 extent=(lons[0],lons[-1],282,0))
ax.set_yticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_yticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_ylim(282,180)
ax.axvline(-96.5, linestyle='-', lw=1.5, zorder=5, c='k')
ax.axvline(-90, linestyle='-', lw=1.5, zorder=5, c='k')
ax.set_title(u"MidWest Daily High Temperature Departure $^\circ\mathrm{C}$\nHovmöller Diagram")
ax.set_ylabel("1 July - 8 October 2013")
ax.set_xlabel("Longitude $^\circ$E, solid lines are Iowa extent, over 36 - 48.75$^\circ$N")
ax.grid(True)

plt.colorbar(res)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
