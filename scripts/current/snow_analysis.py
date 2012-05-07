"""
IEM Snowfall Analysis Engine
$Id$:
"""
import iemre
import iemplot
import iemdb
import numpy
import mx.DateTime
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

    fp = "/home/ldm/data/gis/images/4326/q2/p24h.png"
    q2 = gdal.Open(fp, 0)
    q2d = numpy.flipud( q2.ReadAsArray()[y0:y1:22,x0:x1:25] )

    return q2d / 25.4 * 12.0 # hard code snow ratio!

def fetch_lsrs():
    vals = []
    lats = []
    lons = []
    # Query LSR Data...
    pcursor.execute("""
    SELECT state, max(magnitude) as val, x(geom) as lon, y(geom) as lat
      from lsrs_2012 WHERE type in ('S') and magnitude > 0 and 
      valid > '2012-01-17 00:00' and valid < '2012-01-18 12:00'
      and x(geom) BETWEEN %s and %s and
      y(geom) BETWEEN %s and %s 
      GROUP by state, lon, lat
    """,(iemre.WEST, iemre.EAST, iemre.SOUTH, iemre.NORTH))
    for row in pcursor:
        vals.append( row[1] )
        lats.append( row[3] )
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
    day in ('2012-01-19', '2012-01-20') and snow >= 0 and 
    x(geom) BETWEEN %s and %s and
    y(geom) BETWEEN %s and %s  
    GROUP by id, lon, lat
    """, (iemre.WEST, iemre.EAST, iemre.SOUTH, iemre.NORTH))
    for row in icursor:
        vals.append( row[1] )
        lats.append( row[3] )
        lons.append( row[2] )
    return {'vals': vals, 'lats': lats, 'lons': lons}

snowgrid = init_grid() # inches
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

# Analysis and plot, please
cfg = {
 'wkColorMap': 'WhiteBlueGreenYellowRed',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "16-17 January 2012 - IEM Snowfall Total Analysis",
 '_valid'             : "Snowfall totals up until 8 AM 18 Jan 2012",
 #'_MaskZero'          : True,
 'lbTitleString'      : "[in]",
  '_showvalues'        : False,
 '_format'            : '%.1f',
 '_midwest'         : True,
}
# Generates tmp.ps

tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)
#tmpfp = iemplot.simple_grid_fill(iemre.XAXIS, iemre.YAXIS, snowgrid, cfg)
pqstr = "plot c 000000000000 lsr_snowfall.png bogus png"
thumbpqstr = "plot c 000000000000 lsr_snowfall_thumb.png bogus png"
#iemplot.postprocess(tmpfp,pqstr, thumb=True, thumbpqstr=thumbpqstr)
iemplot.makefeature(tmpfp)
