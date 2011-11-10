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
sources = []
icursor.execute("""
    SELECT id, sum(snow), x(geom) as lon, y(geom) as lat, count(*) from
    summary_2011 t JOIN stations s ON (s.iemid = t.iemid) where network ~* 'COOP' and day in ('2011-11-09') and snow >= 0 and 
    x(geom) BETWEEN %s and %s and
    y(geom) BETWEEN %s and %s  
    GROUP by station, lon, lat
""", (iemplot.MW_WEST, iemplot.MW_EAST, iemplot.MW_SOUTH, iemplot.MW_NORTH))
for row in icursor:
    if row[4] == 2:
        vals.append( row[1] )
        lats.append( row[3] )
        lons.append( row[2] )
        sources.append( COOP )


# Query LSR Data...
pcursor.execute("""
    SELECT state, max(magnitude) as val, x(geom) as lon, y(geom) as lat
      from lsrs_2011 WHERE type in ('S') and magnitude > 0 and 
      valid > '2011-11-09 04:00' and valid < '2011-11-10 09:00'
      GROUP by state, lon, lat
""")
for row in pcursor:
    vals.append( row[1] )
    lats.append( row[3] )
    lons.append( row[2] )
    sources.append( LSR )

# Loop thru the data and try to figure out what is good and what is bad...
final_lats = []
final_lons = []
final_vals = []
buffer = 0.45
for lat in numpy.arange(iemplot.MW_SOUTH, iemplot.MW_NORTH, buffer):
  for lon in numpy.arange(iemplot.MW_WEST, iemplot.MW_EAST, buffer):
    lvals = []
    lsources = []
    for j in range(len(lats)):
      if (lats[j] > (lat-(buffer/2.)) and lats[j] < (lat+(buffer/2.)) and
         lons[j] > (lon-(buffer/2.)) and lons[j] < (lon+(buffer/2.)) ):
        lvals.append( vals[j] )
        lsources.append( sources[j] )
    if len(lvals) == 0:
        # Loop again, but use 2x buffer search...
        for j in range(len(lats)):
            if (lats[j] > (lat-(buffer)) and lats[j] < (lat+(buffer)) and
                lons[j] > (lon-(buffer)) and lons[j] < (lon+(buffer)) ):
                lvals.append( vals[j] )
                lsources.append( sources[j] )
        if len(lvals) == 0:
            final_vals.append( 0.0 )
        else:
            final_vals.append( max(lvals) )
    else:
        final_vals.append( max(lvals) )
    final_lats.append( lat )
    final_lons.append( lon )

# Analysis and plot, please
cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "9 November 2011 - IEM Snowfall Total Analysis",
 '_valid'             : "Snowfall totals up until 9 PM 9 Nov 2011",
 '_MaskZero'          : True,
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
