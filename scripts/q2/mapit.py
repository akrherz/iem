import Image
from pyiem.plot import MapPlot
from pylab import imread
import numpy as np
import matplotlib.cm as cm
import matplotlib.patheffects as PathEffects

img = Image.open("/mesonet/ARCHIVE/data/2013/06/23/GIS/q2/p72h_201306231000.png")
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

m = MapPlot(sector='custom', north=44., east=-89., south=42., west=-93.,
            title='NOAA NMQ 72 Hour Precipitation Estimate',
            subtitle='5 AM 20 Jun 2013 to 5 AM 23 Jun 2013')
cmap = cm.get_cmap('spectral')
cmap.set_under('#FFFFFF')
m.pcolormesh(x, y, data, np.array([0.01,0.25,0.5,1,2,3,4,5,6,7,8,9,10,11,12,13,14]),
             cmap=cmap)
m.map.drawcounties(zorder=10, linewidth=1.)

x, y = m.map([-90.70914,-91.74331,-92.40129], [42.39835,43.27552,42.55437])
txt = m.ax.text(x[0], y[0], "Dubuque", zorder=11, fontsize=18, color='w')
txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground="k")])
txt = m.ax.text(x[1], y[1], "Decorah", zorder=11, fontsize=18, color='w')
txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground="k")])
txt = m.ax.text(x[2], y[2], "Waterloo", zorder=11, fontsize=18, color='w')
txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground="k")])

m.postprocess(filename='test.svg')
import iemplot
iemplot.makefeature('test')