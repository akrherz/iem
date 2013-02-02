"""
IEM Snowfall Analysis Engine

"""
import iemre
import iemplot
import iemdb
import numpy
import random
import mx.DateTime
from iem.plot import MapPlot
import gdal

IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()
POSTGIS = iemdb.connect('postgis', bypass=True)
pcursor = POSTGIS.cursor()

def lalo2pt(lat, lon):
    x = int(( -130.0 - lon ) / - 0.01 )
    y = int(( 55.0 - lat ) / 0.01 )
    return x, y

def sg2pt(lon, lat):
    x = int(( lon - iemre.WEST  ) / 0.25 ) 
    y = int(( lat - iemre.SOUTH  ) / 0.22 )
    return x, y


def init_grid():
    """
    Initialize the grid with Q2 data!
    """
    lat0 = iemre.SOUTH
    lat1 = iemre.NORTH
    lon0 = iemre.WEST
    lon1 = iemre.EAST
    x0, y0 = lalo2pt(lat1, lon0)
    x1, y1 = lalo2pt(lat0, lon1)

    fp = "/home/ldm/data/gis/images/4326/q2/p48h.png"
    q2 = gdal.Open(fp, 0)
    q2d = numpy.flipud( q2.ReadAsArray()[y0:y1:22,x0:x1:25] )

    return q2d / 25.4 # hard code snow ratio!

def fetch_lsrs():
    vals = []
    lats = []
    lons = []
    # Query LSR Data...
    pcursor.execute("""
    SELECT state, max(magnitude) as val, x(geom) as lon, y(geom) as lat
      from lsrs_2012 WHERE type in ('S') and magnitude > 0 and 
      valid > '2012-12-09 00:00' and valid < '2012-12-10 12:00'
      and x(geom) BETWEEN %s and %s and
      y(geom) BETWEEN %s and %s 
      GROUP by state, lon, lat
    """,(iemre.WEST, iemre.EAST, iemre.SOUTH, iemre.NORTH))
    for row in pcursor:
        vals.append( row[1] )
        lats.append( row[3] + (random.random() * 0.01)) 
        lons.append( row[2] )
    return {'vals': vals, 'lats': lats, 'lons': lons}

def fetch_coop():
    vals = []
    lats = []
    lons = []
    icursor.execute("""
    SELECT id, sum(snow), x(geom) as lon, y(geom) as lat, count(*) from
    summary_2012 t JOIN stations s ON (s.iemid = t.iemid) where 
    (network ~* 'COOP' or network ~* 'COCORAHS') and 
    day in ('2012-12-09', '2012-12-10') and snow >= 0 and 
    x(geom) BETWEEN %s and %s and
    y(geom) BETWEEN %s and %s  
    GROUP by id, lon, lat ORDER by sum DESC
    """, (iemre.WEST, iemre.EAST, iemre.SOUTH, iemre.NORTH))
    for row in icursor:

        vals.append( row[1] )
        lats.append( row[3] )
        lons.append( row[2] )
    return {'vals': vals, 'lats': lats, 'lons': lons}

snowgrid = init_grid() # inches
"""
lsrs = fetch_lsrs()
coop = fetch_coop()

lats = []
lons = []
vals = []

for i in range(len(lsrs['vals'])):
    x, y = sg2pt(lsrs['lons'][i], lsrs['lats'][i])
    #print snowgrid[y,x], lsrs['vals'][i], x, y, lsrs['lons'][i], lsrs['lats'][i]
    sg = snowgrid[y,x]
    if lsrs['vals'][i] > sg:
        lats.append( lsrs['lats'][i] )
        lons.append( lsrs['lons'][i] )
        vals.append( lsrs['vals'][i] )
"""


mp = MapPlot(sector='midwest')
mp.contourf(iemre.XAXIS, iemre.YAXIS, snowgrid, range(0,20))
mp.postprocess(view=True)