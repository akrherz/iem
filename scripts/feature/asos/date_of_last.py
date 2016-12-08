import psycopg2
from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot
nt = NetworkTable(['IA_ASOS', 'AWOS'])
pgconn = psycopg2.connect(database='iem', host='iemdb', user='nobody')
cursor = pgconn.cursor()

lats = []
lons = []
vals = []

cursor.execute("""SELECT id, max(day) from summary_2015 s JOIN stations t
 ON (t.iemid = s.iemid) WHERE t.network in ('IA_ASOS', 'AWOS')
 and min_tmpf < 31.5 and day < '2015-04-22' GROUP by id ORDER by max ASC""")

for row in cursor:
    lats.append(nt.sts[row[0]]['lat'])
    lons.append(nt.sts[row[0]]['lon'])
    vals.append(row[1].strftime("%-d %b"))

m = MapPlot(axisbg='white',
            title='Iowa ASOS/AWOS Last Date of Sub-Freezing Temperature',
            subtitle='thru 12 AM 22 April 2015')
m.plot_values(lons, lats, vals, fmt='%s')
m.drawcounties()
m.postprocess(filename='150422.png')
