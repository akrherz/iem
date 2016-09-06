import pygrib
from pyiem.plot import MapPlot
from pyiem import reference
import numpy as np
from pyiem.datatypes import distance

g = pygrib.open('p168m_2016090600f168.grb')

grb = g[1]
lats, lons = grb.latlons()

m = MapPlot(sector='custom', project='aea',
            south=reference.MW_SOUTH, north=reference.MW_NORTH,
            east=reference.MW_EAST, west=reference.MW_WEST,
            axisbg='tan',
            title=("Weather Prediction Center (WPC) "
                   "7 Day Forecasted Precipitation"),
            subtitle='7 PM 5 September thru 7 PM 12 September 2016')

m.contourf(lons, lats, distance(grb['values'], 'MM').value('IN'),
           np.arange(0, 4.6, 0.25), units='inches')

m.postprocess(filename='test.png')
