import datetime
import psycopg2
from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot
nt = NetworkTable(['IA_ASOS', 'AWOS'])
pgconn = psycopg2.connect(database='iem', host='iemdb', user='nobody')
cursor = pgconn.cursor()

lats = []
lons = []
vals = []

cursor.execute("""WITH today as (
    SELECT id, max_tmpf from summary_2017 s JOIN stations t
    ON (s.iemid = t.iemid) WHERE t.network in ('IA_ASOS', 'AWOS')
    and day = '2017-01-18'),
    agg as (
    SELECT t.id, max(day) from summary s, stations t, today t2
    WHERE s.iemid = t.iemid and t.id = t2.id and
    t.network in ('IA_ASOS', 'AWOS') and day > '2016-12-01'
    and day < '2017-01-18' and s.max_tmpf >= t2.max_tmpf
    GROUP by t.id)
    SELECT id, max from agg ORDER by max ASC
    """)

colors = []
for row in cursor:
    lats.append(nt.sts[row[0]]['lat'])
    lons.append(nt.sts[row[0]]['lon'])
    vals.append(row[1].strftime("%-m/%-d"))
    colors.append('r' if row[1] == datetime.date(2016, 12, 25) else 'k')

m = MapPlot(continentalcolor='white',
            title=("Iowa ASOS/AWOS Last Date of as Warm of "
                   "Daily High as 18 Jan 2017"))
m.plot_values(lons, lats, vals, fmt='%s', color=colors, labelbuffer=5)
m.drawcounties()
m.postprocess(filename='170119.png')
