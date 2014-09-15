# Month percentile 
import iemdb, network
import iemplot
from pyiem.plot import MapPlot
import matplotlib.cm as cm
nt = network.Table("IACLIMATE")
COOP = iemdb.connect("coop", bypass=True)
ccursor = COOP.cursor()
ccursor.execute("""
  SELECT station, max(case when year = 2013 then rank else -1 end) as ma, count(*),
  max(case when year = 2013 then  m else -1 end) from 
  (SELECT station, year, m, rank() over (partition by station ORDER by m ASC)
  from
    (SELECT station, year, min(low) as m from alldata_ia where
     month > 6 and sday < '0925' and year > 1950 GROUP by station, year) as foo
  ) as foo2 WHERE station != 'IA0000' and substr(station,3,1) != 'C' 
  GROUP by station ORDER by ma DESC
""")
lats = []
lons = []
vals = []
for row in ccursor:

    if not nt.sts.has_key(row[0]):
        continue
    if row[1] < 0 or row[2] < 60 or row[0] in ['IA2364',]:
        continue
    print row
    #vals.append( float(row[3]) / float(row[4]) * 100.0 )
    vals.append( row[1] / float(row[2]) * 100.0 )
    lats.append( nt.sts[row[0]]['lat'] )
    lons.append( nt.sts[row[0]]['lon'] )

import numpy as np
m = MapPlot(sector='iowa', title='Fall Minimum Temperature Percentile [100=warmest]',
            subtitle='thru 24 September, 2013 vs 1951-2012')
cmap = cm.get_cmap('jet')
m.contourf(lons, lats, vals, np.arange(0,101,10), cmap=cmap)
m.plot_values(lons, lats, vals, '%.0f')
m.drawcounties()
m.postprocess(filename='test.ps')
iemplot.makefeature('test')