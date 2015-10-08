# Month percentile 
import psycopg2
from pyiem.plot import MapPlot
import matplotlib.cm as cm
from pyiem.network import Table as NetworkTable
import numpy as np

nt = NetworkTable("IACLIMATE")
COOP = psycopg2.connect(database="coop", host='iemdb', user='nobody')
ccursor = COOP.cursor()
ccursor.execute("""
  SELECT station, max(case when year = 2015 then rank else -1 end) as ma, count(*),
  max(case when year = 2015 then  m else -1 end) from 
  (SELECT station, year, m, rank() over (partition by station ORDER by m ASC)
  from
    (SELECT station, year, max(high) as m from alldata_ia where
     sday < '0520' and year > 1950 GROUP by station, year) as foo
  ) as foo2 WHERE station != 'IA0000' and substr(station,3,1) != 'C' 
  GROUP by station ORDER by ma DESC
""")
lats = []
lons = []
vals = []
for row in ccursor:
    if row[0] not in nt.sts:
        continue
    if row[1] > 30:
        continue
    print row
    vals.append( row[1] / float(row[2]) * 100.0 )
    lats.append( nt.sts[row[0]]['lat'] )
    lons.append( nt.sts[row[0]]['lon'] )

m = MapPlot(sector='iowa', title='Spring Maximum Temperature Percentile [100=warmest]',
            subtitle='thru 19 May, 2015 vs 1951-2014', axisbg='white')
cmap = cm.get_cmap('jet')
m.contourf(lons, lats, vals, np.arange(0,101,10), cmap=cmap)
m.plot_values(lons, lats, vals, '%.0f')
m.drawcounties()
m.postprocess(filename='test.png')
