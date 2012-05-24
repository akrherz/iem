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
    SELECT id, sum(snow), x(geom) as lon, y(geom) as lat, count(*) from
    summary_2012 t JOIN stations s ON (s.iemid = t.iemid) where 
    (network ~* 'COOP' or network ~* 'COCORAHS') and 
    day in ('2012-03-05') and snow >= 0 and 
    x(geom) BETWEEN %s and %s and
    y(geom) BETWEEN %s and %s  
    GROUP by id, lon, lat
""", (iemplot.MW_WEST, iemplot.MW_EAST, iemplot.MW_SOUTH, iemplot.MW_NORTH))
for row in icursor:
    #if row[4] < 2:
    #    continue
    #if row[1] in [2.6,]:
    #    continue
    vals.append( row[1] )
    lats.append( row[3] )
    lons.append( row[2] )


# Query LSR Data...
pcursor.execute("""
    SELECT state, max(magnitude) as val, x(geom) as lon, y(geom) as lat
      from lsrs_2012 WHERE type in ('S') and magnitude > 0 and 
      valid > '2012-03-04 06:00' and valid < '2012-03-25 12:00'
      GROUP by state, lon, lat
""")
for row in pcursor:
    if row[3] in lats and row[2] in lons:
      continue
    vals.append( row[1] )
    lats.append( row[3] )
    lons.append( row[2] )
    if row[1] in [2.6,]:
        continue

final_lats = lats
final_lons = lons
final_vals = vals
"""
# Loop thru the data and try to figure out what is good and what is bad...
final_lats = []
final_lons = []
final_vals = []
buffer = 0.65
for lat in numpy.arange(iemplot.MW_SOUTH, iemplot.MW_NORTH, buffer):
  for lon in numpy.arange(iemplot.MW_WEST, iemplot.MW_EAST, buffer):
    lvals = []
    for j in range(len(lats)):
      if (lats[j] > (lat-(buffer/2.)) and lats[j] < (lat+(buffer/2.)) and
         lons[j] > (lon-(buffer/2.)) and lons[j] < (lon+(buffer/2.)) ):
        lvals.append( vals[j] )
    if len(lvals) == 0:
        # Loop again, but use 2x buffer search...
        for j in range(len(lats)):
            if (lats[j] > (lat-(buffer)) and lats[j] < (lat+(buffer)) and
                lons[j] > (lon-(buffer)) and lons[j] < (lon+(buffer)) ):
                lvals.append( vals[j] )
        if len(lvals) == 0:
            final_vals.append( 0.0 )
        else:
            final_vals.append( max(lvals) )
    else:
        final_vals.append( max(lvals) )
    final_lats.append( lat )
    final_lons.append( lon )
"""
# Analysis and plot, please
cfg = {
 'wkColorMap': 'WhiteBlueGreenYellowRed',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "4 March 2012 - IEM Snowfall Total Analysis",
 '_valid'             : "Snowfall totals up until 8 AM 5 Mar 2012",
 #'_MaskZero'          : True,
 'lbTitleString'      : "[in]",
  '_showvalues'        : False,
 '_format'            : '%.1f',
# '_midwest'         : True,
}
# Generates tmp.ps
tmpfp = iemplot.simple_contour(final_lons, final_lats, final_vals, cfg)
pqstr = "plot c 000000000000 lsr_snowfall.png bogus png"
thumbpqstr = "plot c 000000000000 lsr_snowfall_thumb.png bogus png"
#iemplot.postprocess(tmpfp,pqstr, thumb=True, thumbpqstr=thumbpqstr)
iemplot.makefeature(tmpfp)
