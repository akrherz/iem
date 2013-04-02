# Generate a clean snowfall analysis, please...

import iemplot
import iemdb
import numpy
import mx.DateTime

IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()
POSTGIS = iemdb.connect('postgis', bypass=True)
pcursor = POSTGIS.cursor()

# Query COOP Data...
(COOP, LSR) = (1,2)
vals = []
lats = []
lons = []
icursor.execute("""
    SELECT id, sum(snow), 
    x(geom) as lon, 
    y(geom) as lat, count(*) from
    summary_2013 t JOIN stations s ON (s.iemid = t.iemid) where 
    (network ~* 'COOP' or network ~* 'COCORAHS') and 
    day in ('2014-01-30', '2014-01-31') and snow >= 0 and 
    x(geom) BETWEEN %s and %s and
    y(geom) BETWEEN %s and %s  
    GROUP by id, lon, lat
""", (iemplot.MW_WEST, iemplot.MW_EAST, iemplot.MW_SOUTH, iemplot.MW_NORTH))
for row in icursor:
    #if row[4] < 2:
    #    continue
    if row[3] in lats and row[2] in lons:
        continue
    if row[1] == 0.2:
        continue
    vals.append( row[1] )
    lats.append( row[3] )
    lons.append( row[2] )


# Query LSR Data...
pcursor.execute("""
    SELECT state, max(magnitude) as val, 
        x(geom) as lon, 
       y(geom) as lat
      from lsrs_2013 WHERE typetext in ('FREEZING RAIN') and magnitude > 0 and 
      valid > '2013-01-27 00:00' and valid < '2013-01-28 06:00' and state='IA'
      GROUP by state, lon, lat ORDER by val DESC
""")
for row in pcursor:
    if row[3] in lats and row[2] in lons:
        continue
    skip = False
    for lo, la in zip(lons, lats):
        if abs(row[2] - lo) < 0.2 and abs(row[3] - la) < 0.1:
            skip = True
            break
    if skip:
        print 'skipping'
        continue
    vals.append( row[1] )
    lats.append( row[3] )
    lons.append( row[2] )

dx = 0.65
dy = 0.65
nx = int((iemplot.MW_EAST - iemplot.MW_WEST) / dx) + 1
ny = int((iemplot.MW_NORTH - iemplot.MW_SOUTH) / dy) + 1
xaxis = numpy.linspace(iemplot.MW_WEST, iemplot.MW_EAST, nx)
yaxis = numpy.linspace(iemplot.MW_SOUTH, iemplot.MW_NORTH, ny)
grid = numpy.zeros( (ny,nx), 'f')

for lo, la, val in zip(lons, lats, vals):
    gridx = int((lo - iemplot.MW_WEST) / dx)
    gridy = int((la - iemplot.MW_SOUTH) / dy)
    if gridx >= nx or gridy >= ny:
        continue
    if val > grid[gridy,gridx]:
        grid[gridy,gridx] = val

# Analysis and plot, please
cfg = {
 'wkColorMap': 'WhiteBlueGreenYellowRed',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "27 January 2013 - Freezing Rain Reports (inch)",
# '_valid'             : "",
 #'_MaskZero'          : True,
 'lbTitleString'      : "[in]",
  '_showvalues'        : False,
 'cnLevelSelectionMode': "ExplicitLevels",
 'cnLevels' : [0.01,0.1,0.25,0.5,1,2,3,5,7,9,11,13,15,17],

 '_format'            : '%.2f',
# '_midwest'         : True,
}
# Generates tmp.ps
#tmpfp = iemplot.simple_grid_fill(xaxis, yaxis, grid, cfg)
tmpfp = iemplot.simple_valplot(lons, lats, vals, cfg)
pqstr = "plot c 000000000000 lsr_snowfall.png bogus png"
thumbpqstr = "plot c 000000000000 lsr_snowfall_thumb.png bogus png"
#iemplot.postprocess(tmpfp,pqstr, thumb=True, thumbpqstr=thumbpqstr)
iemplot.makefeature(tmpfp)
