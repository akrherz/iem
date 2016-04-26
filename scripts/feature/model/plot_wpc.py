import pygrib
from pyiem.plot import MapPlot
import numpy as np
from pyiem.datatypes import distance

g = pygrib.open('/tmp/p168m_2016042600f168.grb')

grb = g[1]
lats, lons = grb.latlons()

m = MapPlot(sector='midwest', axisbg='tan',
            title=("Weather Prediction Center (WPC) "
                   "7 Day Forecasted Precipitation"),
            subtitle='7 PM 25 April thru 7 PM 2 May 2016')

m.contourf(lons, lats, distance(grb['values'], 'MM').value('IN'),
           np.arange(0, 4.6, 0.25), units='inches')

m.postprocess(filename='test.png')
