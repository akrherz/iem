import psycopg2
import network
import numpy as np
from pyiem.plot import MapPlot
nt = network.Table(("IACLIMATE"))
import matplotlib.cm as cm
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()

cursor.execute("""
  select station, sum(case when year = 2013 then precip else 0 end),
  sum(case when year = 2012 then precip else 0 end) from alldata_ia where 
  year > 2011 and month in (6,7,8) and sday < '0807' 
  and substr(station,2,1) != 'C' and station != 'IA0000' GROUP by station
""")
vals = []
lats = []
lons = []
vals2 = []
for row in cursor:
    print row
    if row[1] < 0.1 or row[2] < 0.1:
        continue
    lats.append( nt.sts[row[0]]['lat'])
    lons.append( nt.sts[row[0]]['lon'])
    vals.append( row[1] - row[2])
    vals2.append( row[1] - row[2] )

m = MapPlot(sector='iowa',
            title='1 June - 6 August 2013 vs 2012 Precipitation',
            subtitle='Difference labeled [inch]')
cmap = cm.get_cmap('Spectral')
cmap.set_over('#ffffff')
m.contourf(lons, lats, vals, np.array([-10,-6,-4,-3,-2,-1,0,1,2,3,4,6,10]), cmap=cmap, units='(2013 - 2012) inches')
m.plot_values(lons, lats, vals2, '%.2f')
m.drawcounties()

m.postprocess(filename='test.ps')
import iemplot
iemplot.makefeature('test')
