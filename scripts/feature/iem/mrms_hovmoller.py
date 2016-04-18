import os
import datetime
import gdal
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap  # nopep8 @UnresolvedImport
import matplotlib.colors as mpcolors

sts = datetime.datetime(2016, 4, 15, 5)
ets = datetime.datetime(2016, 4, 18, 13)
interval = datetime.timedelta(hours=1)

ULX = -130.
ULY = 55.
WEST = -104.
EAST = -80.
SOUTH = 35.
NORTH = 48.

X0 = int((WEST - ULX) * 100.)
X1 = int((EAST - ULX) * 100.)
Y0 = int((ULY - NORTH) * 100.)
Y1 = int((ULY - SOUTH) * 100.)
t = int((ets - sts).total_seconds() / 3600.)

if not os.path.isfile('res.npy'):
    res = np.zeros((t, X1-X0), 'f')
    now = sts
    i = 0
    total = np.zeros((Y1-Y0, X1-X0), 'f')
    while now < ets:
        fn = now.strftime(("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/mrms/"
                           "p1h_%Y%m%d%H%M.png"))
        p1h = gdal.Open(fn)
        p1h = p1h.ReadAsArray()[Y0:Y1, X0:X1]
        mm = np.where(p1h >= 254, 0, p1h)
        mm = np.where(np.logical_and(p1h >= 180,
                                     p1h < 244), 125. + (p1h - 180) * 5., mm)
        mm = np.where(np.logical_and(p1h >= 100,
                                     p1h < 180), 25. + (p1h - 100) * 1.25, mm)
        mm = np.where(np.logical_and(p1h >= 0,
                                     p1h < 100), p1h * 0.25, mm)
        res[i, :] = np.average(mm, 0)
        total += mm
        print now, np.max(total), np.max(mm)
        now += interval
        i += 1
    np.save('res.npy', res)
    np.save('total.npy', total)
else:
    res = np.load('res.npy')
    total = np.load('total.npy')


(fig, ax) = plt.subplots(2, 1)

b = Basemap(projection='merc', fix_aspect=False,
            urcrnrlat=NORTH,
            llcrnrlat=SOUTH,
            urcrnrlon=EAST,
            llcrnrlon=WEST,
            resolution='i', ax=ax[0])
cmap = plt.get_cmap('jet')
cmap.set_under('white')
clevs = [0.01, 0.25, 0.5, 0.75, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]
norm = mpcolors.BoundaryNorm(clevs, cmap.N)
r = b.imshow(np.flipud(total) / 25.4, aspect='auto', norm=norm,
             cmap=cmap, interpolation='nearest',
             extent=(WEST, EAST, SOUTH, NORTH))
b.drawstates(linewidth=1., color='k')
b.drawcounties(color='k')
b.drawcountries(color='k')
plt.colorbar(r, ax=ax[0])
ax[0].set_title(("NOAA MRMS Q3 ::15 Apr 12:00 AM to 18 Apr 7:00 AM\n"
                 "Total Precipitation [inches]"))

# -------------------------------------------------------------------

cmap = plt.get_cmap('jet')
cmap.set_under('white')
clevs = np.arange(0.01, 0.14, 0.01)
norm = mpcolors.BoundaryNorm(clevs, cmap.N)
r = ax[1].imshow(res / 25.4, norm=norm, cmap=cmap,
                 aspect='auto', interpolation='nearest',
                 extent=(WEST, EAST, t, 0))
plt.colorbar(r, ax=ax[1])
ax[1].axvline(-96.5, linestyle='-', lw=1.5, zorder=5, c='k')
ax[1].axvline(-90, linestyle='-', lw=1.5, zorder=5, c='k')

yticks = []
yticklabels = []
now = sts
i = 0
while now < ets:
    lts = now - datetime.timedelta(hours=5)
    if lts.hour % 6 == 0:
        yticks.append(i)
        yticklabels.append(lts.strftime("%-d %b %I %p"))
    i += 1
    now += interval

ax[1].set_yticks(yticks)
ax[1].set_yticklabels(yticklabels, fontsize=10)
ax[1].grid(True)
ax[1].set_title("Hovmoller Diagram [inch/hr]")
ax[1].set_xlabel(("Longitude [$^\circ$E] "
                  "vertical lines are Iowa's east/west extent"))

fig.savefig('test.png')
