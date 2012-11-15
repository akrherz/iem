# Generate current plot of air temperature

import sys, os
from iem.plot import MapPlot
import mx.DateTime
import iemdb
import numpy
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

vals = []
lats = []
lons = []
valmask = []
icursor.execute("""SELECT id, network, x(geom) as lon, y(geom) as lat, min(min_tmpf) 
    from summary_2012 s JOIN stations t on (t.iemid = s.iemid) 
    WHERE network IN ('IA_ASOS','AWOS', 'IL_ASOS', 'MO_ASOS', 'KS_ASOS',
    'NE_ASOS', 'SD_ASOS', 'MN_ASOS', 'WI_ASOS') and min_tmpf > 0 and 
    day > '2012-08-01' and id not in ('SLB', 'BNW') 
    GROUP by id, network, lon, lat ORDER by min DESC""")
for row in icursor:
  vals.append( row[4] )
  lats.append( row[3] )
  lons.append( row[2] )
  valmask.append( row[1] in ['IA_ASOS', 'AWOS'] )
  print row[3], row[0]

m = MapPlot(title="2012 Fall Minimum Temperature after 1 August",
 subtitle='Valid 1 Aug - %s' % (mx.DateTime.now().strftime("%d %b %Y"),),
 figsize=(3.2,2.4)
)
m.contourf(lons, lats, vals, numpy.arange(10,34,2))
m.plot_values(lons, lats, vals, '%.0f', valmask)
m.drawcounties()
m.postprocess(view=True, filename='121105_s.png')