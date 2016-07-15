import pygrib
from pyiem.plot import MapPlot
import numpy as np
from pyiem.datatypes import temperature

g = pygrib.open('gfs.grib')

grb = g[1]
lats, lons = grb.latlons()

lons = np.where(lons > 180, lons - 360, lons)

m = MapPlot(sector='midwest', axisbg='tan',
            title=("NCEP Global Forecast System (GFS) "
                   "2m Air Temp valid 4 PM 22 July 2016"),
            subtitle='195 Hour Forecast from 18 UTC run on 14 July 2016',
            titlefontsize=16)

t = temperature(grb['values'], 'K').value('F')
m.contourf(lons, lats, t,
           np.arange(74, 117, 2), units='F')

m.postprocess(filename='test.png')
