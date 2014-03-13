import psycopg2
import numpy as np
from pyiem.plot import MapPlot
import network
nt = network.Table("IACLIMATE")
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()

cursor.execute("""
 SELECT station, rank from
(SELECT station, year, rank() over (PARTITION by station ORDER by avg ASC) from
(SELECT station, year, avg((high+low)/2.0) from alldata_ia where sday <= '0312'
 and 
 station in (select distinct station from alldata_ia where year = 1893)
 GROUP by station, year) as foo 
 ) as foo2 WHERE year = 2014

""")
lats = []
lons = []
ranks = []
for row in cursor:
    if row[0] in ['IA2364', 'IA1635']:
        continue
    lats.append( nt.sts[row[0]]['lat'] )
    lons.append( nt.sts[row[0]]['lon'] )
    ranks.append( row[1] )

m = MapPlot(title='1 Jan - 12 Mar 2014 Average Temperature Rank',
            subtitle='1 is coldest, for period 1893-2014')
m.plot_values(lons, lats, ranks, textsize=20)
m.drawcounties()

m.postprocess(filename='test.ps')
import iemplot
iemplot.makefeature('test')
