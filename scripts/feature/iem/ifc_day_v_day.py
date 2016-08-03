import netCDF4
from pyiem.iemre import daily_offset
import datetime
import numpy as np
import matplotlib.pyplot as plt
from pyiem.datatypes import distance
from matplotlib.colors import LogNorm

day1 = datetime.date(2016, 8, 1)
day2 = datetime.date(2016, 8, 2)

nc = netCDF4.Dataset("/mesonet/data/iemre/2016_ifc_daily.nc")
idx1 = daily_offset(day1)
idx2 = daily_offset(day2)

x = np.digitize([-96.64, -90.14], nc.variables['lon'][:])
y = np.digitize([40.37, 43.50], nc.variables['lat'][:])

rain1 = distance(nc.variables['p01d'][idx1, y[0]:y[1], x[0]:x[1]],
                 'MM').value('IN')
rain2 = distance(nc.variables['p01d'][idx2, y[0]:y[1], x[0]:x[1]],
                 'MM').value('IN')

(fig, ax) = plt.subplots(1, 1)

(H2, xedges, yedges) = np.histogram2d(rain1.ravel(), rain2.ravel(),
                                      bins=75)

# H2[0:3, 0] = 0
# H2[0, 0:3] = 0
H2 = np.ma.array(H2.transpose())
H2.mask = np.where(H2 < 1, True, False)
extent = [xedges[0], xedges[-1], yedges[-1], yedges[0]]
res = ax.imshow(H2,  extent=extent, interpolation='nearest',
                norm=LogNorm(vmin=1, vmax=10000))
ax.set_ylim(0, yedges[-1])
ax.grid(True)
ax.set_title(("Iowa Flood Center Iowa Gridded Precip Estimates\n"
              "2 Aug vs 1 Aug 2016 Coverage, ~0.005$^\circ$ cell size"))
ax.set_xlabel("1 August 2016 Total [inch]")
ax.set_ylabel("2 August 2016 Total [inch]")
fig.colorbar(res, label='grid cells')

fig.savefig('160803.png')
