from PIL import Image
from pyiem.plot import MapPlot
import numpy as np
import matplotlib.patheffects as PathEffects

img = Image.open("p48h_201410150000.png")
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

m = MapPlot(sector='iowa', 
            title='NOAA MRMS 48 Hour Precipitation Estimate',
            subtitle='7 PM 12 Oct 2014 to 7 PM 14 Oct 2014')
clevs = np.arange(0,0.2,0.05)
clevs = np.append(clevs, np.arange(0.2, 1.0, 0.1))
clevs = np.append(clevs, np.arange(1.0, 5.0, 0.25))
clevs = np.append(clevs, np.arange(5.0, 10.0, 1.0))
clevs[0] = 0.01
m.pcolormesh(x, y, data, clevs)
m.map.drawcounties(zorder=10, linewidth=1.)


m.postprocess(filename='test.ps')
import iemplot
iemplot.makefeature('test')
