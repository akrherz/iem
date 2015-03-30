import psycopg2
from pyiem.plot import MapPlot
import datetime
import pytz
import numpy as np

pgconn2 = psycopg2.connect(database='iem', host='iemdb', user='nobody')
cursor2 = pgconn2.cursor()

cursor2.execute("""
 SELECT id, extract(year from day) as yr,
 sum(case when max_sknt >= (40. / 1.15) or max_gust >= (40. / 1.15) then 1 else 0 end)
 from summary s JOIN stations t on (t.iemid = s.iemid)
 WHERE t.network in ('IA_ASOS', 'AWOS') and day < '2015-01-01-'
 and day > '2008-01-01'
 GROUP by id, yr
""")
hits = {}
for row in cursor2:
    stid = row[0]
    if stid not in hits:
        hits[stid] = []
    hits[stid].append(row[2])

from pyiem.network import Table as NetworkTable

nt = NetworkTable(('IA_ASOS', 'AWOS'))

vals = []
lats = []
lons = []
for station in hits:
    lats.append(nt.sts[station]['lat'])
    lons.append(nt.sts[station]['lon'])
    vals.append(np.average(hits[station]))

m = MapPlot(sector='iowa', axisbg='white',
            title="Average Number of Days per Year with Peak Wind Gust over 40 MPH",
            subtitle="Based on IEM Archives of Iowa ASOS/AWOS Data (2008-2014)")
m.plot_values(lons, lats, vals, '%.1f')
m.drawcounties()
m.postprocess(filename='test.png')