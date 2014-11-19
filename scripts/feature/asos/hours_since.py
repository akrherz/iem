import psycopg2
from pyiem.plot import MapPlot
import datetime
import pytz

pgconn = psycopg2.connect(database='asos', host='iemdb', user='nobody')
cursor = pgconn.cursor()
pgconn2 = psycopg2.connect(database='iem', host='iemdb', user='nobody')
cursor2 = pgconn2.cursor()

cursor2.execute("""
 SELECT id, max(tmpf) from current_log c JOIN stations t on (t.iemid = c.iemid)
 WHERE c.valid > '2014-11-19' and t.network in ('IA_ASOS','MO_ASOS','IL_ASOS', 'ND_ASOS', 'AWOS',
          'WI_ASOS','MN_ASOS', 'SD_ASOS', 'NE_ASOS', 'KS_ASOS',
          'IN_ASOS','KY_ASOS','OH_ASOS','MI_ASOS') and tmpf >= 32.5
          GROUP by id
""")
hits = []
for row in cursor2:
    hits.append(row[0])

cursor.execute("""SELECT station, max(valid) from t2014 where
 valid > '2014-11-01' and tmpf >= 32.5 GROUP by station ORDER by max ASC""")

from pyiem.network import Table as NetworkTable

nt = NetworkTable(('IA_ASOS','MO_ASOS','IL_ASOS', 'ND_ASOS', 'AWOS',
          'WI_ASOS','MN_ASOS', 'SD_ASOS', 'NE_ASOS', 'KS_ASOS',
          'IN_ASOS','KY_ASOS','OH_ASOS','MI_ASOS'))
now = datetime.datetime.now()
now = now.replace(tzinfo=pytz.timezone("America/Chicago"))
vals = []
lats = []
lons = []
for row in cursor:
    station = row[0]
    if not nt.sts.has_key(station):
        continue
    print station, now - row[1]
    lats.append(nt.sts[station]['lat'])
    lons.append(nt.sts[station]['lon'])
    if station in hits:
        print 'Zero'
        vals.append( 0 )
    else:
        vals.append( ((now - row[1]).days * 24 + (now -row[1]).seconds / 3600.)/24. )
    
m = MapPlot(sector='midwest',
            title="Days since Last 33+$^\circ$F Temperature",
            subtitle="Based on ASOS/AWOS Airport weather stations through 5 AM, 19 Nov")
m.contourf(lons, lats, vals, range(0,13,1), units='days')
m.postprocess(filename='test.png')