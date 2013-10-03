"""
Create a plot of a RTMA variable, this should be easy...
"""
import pygrib
import datetime
from pyiem.plot import MapPlot
import numpy as np
from matplotlib.patches import Polygon

def do_hour(gts, varname):
    """
    Generate an hourly plot of RTMA
    """
    fn = gts.strftime("hrrr.t20z.3kmf00.grib2")
    grib = pygrib.open(fn)
    for g in grib:
        print g['name']
    g = grib[2]
    lats, lons = g.latlons()
    total = ( g["values"] - 273.15 )  * 9.0/5.0 + 32.0

    m = MapPlot('iowa')
    m.drawcounties()
    m.pcolormesh(lons, lats, total, np.arange(60,82,0.5))
    
    m.map.readshapefile('cities', 'cities', ax=m.ax)
    for nshape, seg in enumerate(m.map.cities):
        poly=Polygon(seg, fc='None', ec='k', lw=1.5, zorder=3)
        m.ax.add_patch(poly)

    
    m.postprocess(filename='test.png')

do_hour( datetime.datetime(2011,6,1,17,0), 'TMPK')