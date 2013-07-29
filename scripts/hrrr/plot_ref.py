import pygrib
from pyiem.plot import MapPlot
import numpy as np
import datetime

sts = datetime.datetime(2013,7,9,14)

grbs = pygrib.open('hrrr.ref.201307091900.grib2')

gs = grbs.select(level=0)
i = 0
for g in gs:
    print sts
    lats, lons = g.latlons()
    ref = g['values']

    m = MapPlot(sector='midwest',
                title='9 Jul 2013 19 UTC HRRR Base Reflectivity',
                subtitle='valid: %s' % (sts.strftime("%-d %b %Y %I:%M %P"),))

    m.pcolormesh(lons, lats, ref, np.arange(0,75,5))

    m.postprocess(filename='frame%02i.png' % (i,))
    
    sts += datetime.timedelta(minutes=15)
    i += 1