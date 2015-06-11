import pygrib
from pyiem.plot import MapPlot
import numpy as np
from pyiem.datatypes import distance

g = pygrib.open('p120m_2015061100f120.grb')

grb = g[1]
lats, lons = grb.latlons()

m = MapPlot(sector='midwest',
  title='Weather Prediction Center (WPC) 5 Day Forecasted Precipitation',
  subtitle='7 PM 10 June thru 7 PM 15 June 2015')

m.contourf(lons, lats, distance(grb['values'], 'MM').value('IN'),
           np.arange(0,7.6,0.25), units='inches')

m.postprocess(filename='test.png')
