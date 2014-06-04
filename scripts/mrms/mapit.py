from PIL import Image
from pyiem.plot import MapPlot
import numpy as np
import matplotlib.patheffects as PathEffects

img = Image.open("/mesonet/ARCHIVE/data/2014/06/04/GIS/mrms/p24h_201406041000.png")
data = np.flipud(np.asarray(img))
# 7000,3500 == -130,-60,55,25 ===  -100 to -90 then 38 to 45
sample = data[1800:2501, 3000:4501]
sample = np.where(sample == 255, 0 , sample)
data = sample * 0.01
data = np.where(sample > 100, 1. + (sample  - 100) * 0.05, data)
data = np.where(sample > 180, 5. + (sample  - 180) * 0.2, data)
lons = np.arange(-100, -84.99, 0.01)
lats = np.arange(38, 45.01, 0.01)

x, y = np.meshgrid(lons, lats)

m = MapPlot(sector='custom', north=42.5, east=-93., south=40.5, west=-97.,
            title='NOAA MRMS 24 Hour Precipitation Estimate',
            subtitle='5 AM 3 Jun 2014 to 5 AM 4 Jun 2014')
clevs = np.arange(0,0.2,0.05)
clevs = np.append(clevs, np.arange(0.2, 1.0, 0.1))
clevs = np.append(clevs, np.arange(1.0, 5.0, 0.25))
clevs = np.append(clevs, np.arange(5.0, 10.0, 1.0))
clevs[0] = 0.01
m.pcolormesh(x, y, data, clevs)
m.map.drawcounties(zorder=10, linewidth=1.)

x, y = m.map([-93.65311, -93.90047, -95.89917], [41.53395, 40.63064, 41.31028])
txt = m.ax.text(x[0], y[0], "Des Moines", zorder=11, fontsize=18, color='w', ha='center')
txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground="k")])
txt = m.ax.text(x[1], y[1], "Lamoni", zorder=11, fontsize=18, color='w', ha='center')
txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground="k")])
txt = m.ax.text(x[2], y[2], "Omaha", zorder=11, fontsize=18, color='w', ha='center')
txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground="k")])

m.postprocess(filename='test.ps')
import iemplot
iemplot.makefeature('test')