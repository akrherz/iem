import psycopg2
import network
import numpy as np
from pyiem.plot import MapPlot
nt = network.Table(("IACLIMATE"))
import matplotlib.cm as cm
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()

cursor.execute("""
  select foo.station, foo.sum, foo2.sum from (select station, sum(precip) from 
  alldata_ia where month = 7 and year = 2013 group by station) as foo, 
  (select station, sum(precip) from climate WHERE valid between '2000-07-01' 
  and '2000-07-16' GROUP by station) as foo2 WHERE foo.station = foo2.station
  and substr(foo.station,2,1) != 'C' and substr(foo.station,2,4) != '0000'
  ORDER by foo.sum ASC
""")
vals = []
lats = []
lons = []
vals2  = []
for row in cursor:
    if not nt.sts.has_key(row[0]) or row[0] in ['IA0149', 'IA0200']:
        continue
    print row
    lats.append( nt.sts[row[0]]['lat'])
    lons.append( nt.sts[row[0]]['lon'])
    vals.append( row[1] / row[2] * 100.0)
    vals2.append( row[1] )

m = MapPlot(sector='iowa',
            title='1-15 July 2013 Precipitation Percent of Normal (contour)',
            subtitle='Actual accumulation labeled [inch]')
cmap = cm.get_cmap('Spectral')
cmap.set_over('#ffffff')
m.contourf(lons, lats, vals, np.arange(0,101,10), cmap=cmap)
m.plot_values(lons, lats, vals2, '%.2f')
m.drawcounties()

m.postprocess(filename='test.ps')
import iemplot
iemplot.makefeature('test')