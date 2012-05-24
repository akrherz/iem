# Generate a clean snowfall analysis, please...

import iemplot
import iemdb
import numpy
import mx.DateTime

IEM = iemdb.connect('coop', bypass=True)
icursor = IEM.cursor()

vals = []
lats = []
lons = []
icursor.execute("""
select id, x(geom), y(geom), s.sum from (select station, sum(snow) from climate51 where station ~* '^IA' and (valid > '2000-10-01' or valid < '2000-05-01') GROUP by station) as s JOIN stations t on (t.id = s.station) WHERE s.sum > 0 and t.network = 'IACLIMATE' and t.id NOT IN ('IA8706', 'IA1354', 'IA2203', 'IA5769','IA3980')
""")
for row in icursor:
  vals.append( row[3] )
  lats.append( row[2] )
  lons.append( row[1] )
  

# Analysis and plot, please
cfg = {
 'wkColorMap': 'WhiteBlueGreenYellowRed',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "Winter Average Snowfall Total",
 '_valid'             : "1951-2011 Climatology",
 #'_MaskZero'          : True,
 'lbTitleString'      : "[in]",
  '_showvalues'        : True,
 '_format'            : '%.1f',
# '_midwest'         : True,
}
# Generates tmp.ps
tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)
pqstr = "plot c 000000000000 lsr_snowfall.png bogus png"
thumbpqstr = "plot c 000000000000 lsr_snowfall_thumb.png bogus png"
#iemplot.postprocess(tmpfp,pqstr, thumb=True, thumbpqstr=thumbpqstr)
iemplot.makefeature(tmpfp)
