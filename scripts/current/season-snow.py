# Generate a clean snowfall analysis, please...

import iemplot
import iemdb
import numpy
import Ngl
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
plotvals = []
sources = []
#icursor.execute("""
#   SELECT id, sum(snow), x(geom) as lon, y(geom) as lat, count(*),
#    s.name from
#    summary t JOIN stations s ON (s.iemid = t.iemid) where 
#    (network ~* 'COOP' or network ~* 'COCORAHS') and 
#    day > '2011-10-01' and snow >= 0 and s.state = 'IA' and 
#    x(geom) BETWEEN %s and %s and
#    y(geom) BETWEEN %s and %s  
#    GROUP by id, lon, lat, name
#""", (iemplot.MW_WEST, iemplot.MW_EAST, iemplot.MW_SOUTH, iemplot.MW_NORTH))
#for row in icursor:
#    if row[4] < 2:
#        continue
#    if row[1] in [2.6,]:
#        continue
#    vals.append( row[1] )
#    lats.append( row[3] )
#    lons.append( row[2] )
#    print '%s,%s,%s,%s' % (row[1],row[2],row[3], row[5])
#    sources.append( COOP )
for line in open('data.txt'):
    tokens = line.split(",")
    if float(tokens[0]) < 1:
        continue
    if float(tokens[0]) > 19.9:
        continue
    if float(tokens[0]) < 4:
        print tokens
        continue
    vals.append( float( tokens[0] ) )
    lats.append( float( tokens[2] ) )
    lons.append( float( tokens[1] ) )
    plotvals.append( tokens[3] )
delx = (iemplot.MW_EAST - iemplot.MW_WEST) / (iemplot.MW_NX - 1)
dely = (iemplot.MW_NORTH - iemplot.MW_SOUTH) / (iemplot.MW_NY - 1)
# Create axis
xaxis = iemplot.MW_WEST + delx * numpy.arange(0, iemplot.MW_NX)
yaxis = iemplot.MW_SOUTH + dely * numpy.arange(0, iemplot.MW_NY)

obs = Ngl.natgrid(lons, lats, vals, xaxis, yaxis)

IEM = iemdb.connect('coop', bypass=True)
icursor = IEM.cursor()

vals2 = []
lats2 = []
lons2 = []
icursor.execute("""
select id, x(geom), y(geom), s.sum from (select station, sum(snow) from climate51 where station ~* '^IA' and (valid > '2000-10-01' or valid < '2000-02-17') GROUP by station) as s JOIN stations t on (t.id = s.station) WHERE s.sum > 0 and t.network = 'IACLIMATE' and t.id NOT IN ('IA2999','IA7147','IA4705','IA3509','IA6800','IA1233','IA7312','IA3517','IA7678','IA6940','IA4049','IA8706', 'IA1354', 'IA2203', 'IA5769','IA3980') ORDER by sum ASC
""")
for row in icursor:
  vals2.append( row[3] )
  lats2.append( row[2] )
  lons2.append( row[1] )

climate = Ngl.natgrid(lons2, lats2, vals2, xaxis, yaxis)

# Analysis and plot, please
cfg = {
 #'wkColorMap': 'WhiteBlueGreenYellowRed',
 'wkColorMap': 'nrl_sirkes',
 'nglSpreadColorStart': -1,
 'nglSpreadColorEnd'  : 2,
 '_title'             : "IEM Total Snowfall Departure from Average",
 '_valid'             : "1 Oct 2011 - 16 Feb 2012 against 60 year climatology",
 #'_MaskZero'          : True,
 'lbTitleString'      : "[in]",
  '_showvalues'        : True,
 '_format'            : '%.1f',
 'cnLevelSelectionMode': "ExplicitLevels",
 'cnLevels' : [-16,-12,-8,-4,-1,1,4,8,12,16],
# '_midwest'         : True,
}
# Generates tmp.ps
tmpfp = iemplot.simple_grid_fill(xaxis, yaxis, numpy.transpose(obs - climate), cfg)
#tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)
pqstr = "plot c 000000000000 lsr_snowfall.png bogus png"
thumbpqstr = "plot c 000000000000 lsr_snowfall_thumb.png bogus png"
#iemplot.postprocess(tmpfp,pqstr, thumb=True, thumbpqstr=thumbpqstr)
iemplot.makefeature(tmpfp)
