import psycopg2
import datetime
from pyiem.plot import MapPlot
IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
cursor = IEM.cursor()

cursor.execute("""select station, st_x(geom), st_y(geom),
    max(valid) from
    cli_data c JOIN stations s on (s.id = c.station)
    WHERE s.network = 'NWSCLI' and c.valid > '2016-01-01'
    and low < 32 GROUP by station, st_x, st_y""")

lats = []
lons = []
colors = []
vals = []

base = datetime.date(2016, 4, 15)

for row in cursor:
    if row[3] is None or row[0] in ['KGFK', 'KRAP']:
        continue
    lats.append(row[2])
    lons.append(row[1])
    vals.append(row[3].strftime("%-m/%-d"))
    colors.append('#ff0000' if row[3] < base else '#0000ff')


m = MapPlot(sector='midwest', axisbg='white',
            title="2016 Date of Last Sub 32$^\circ$F Temperature",
            subtitle='2 May 2016 based on NWS issued CLI Reports, pre April 15 dates in red')
m.plot_values(lons, lats, vals, fmt='%s', textsize=12, color=colors,
              labelbuffer=5)
m.postprocess(filename='test.png')

