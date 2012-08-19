import iemdb
import numpy
import numpy.ma
import scipy.stats
import network
nt = network.Table("IACLIMATE")
nt.sts['IA0200']['lon'] += 0.2
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

statewide = []
ccursor.execute("""
 SELECT year, month, sum(precip) from alldata_ia 
 where station = 'IA0000' and year > 1950 and month in (9,10,11) GROUP by year, month
 ORDER by year ASC, month ASC
""")
for row in ccursor:
  statewide.append( row[2] )

cors = []
lats = []
lons = []
for stid in nt.sts.keys():
  if stid == 'IA0000' or stid[2] == 'C' or stid == 'IA0149':
    continue
  ccursor.execute("""
 SELECT year, month, sum(precip) from alldata_ia 
 where station = '%s' and year > 1950 and month in (9,10,11) GROUP by year, month
 ORDER by year ASC, month ASC
  """ % (stid,))
  data = []
  for row in ccursor:
    data.append( row[2] )

  R = numpy.corrcoef(data, statewide)
  print stid, R[0,1], nt.sts[stid]['name']
  lats.append( nt.sts[stid]['lat'] )
  lons.append( nt.sts[stid]['lon'] )
  cors.append( R[0,1] )

cfg = {'lbTitleString': ' ',
  '_title': '1951-2012 SON Monthly Precip Correlation Coefficient',
  '_valid': 'Local Station Against IEM Computed Statewide Areal Average',
 '_showvalues': True,
 '_format': '%.2f'}

import iemplot
tmpfp = iemplot.simple_contour(lons, lats, cors, cfg)

iemplot.makefeature(tmpfp)
