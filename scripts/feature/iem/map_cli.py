import psycopg2
from pyiem.plot import MapPlot
IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
cursor = IEM.cursor()

cursor.execute("""select station, st_x(geom), st_y(geom),
    snow_jul1 - snow_jul1_normal from
    cli_data c JOIN stations s on (s.id = c.station)
    WHERE s.network = 'NWSCLI' and c.valid = '2016-01-20' """)

lats = []
lons = []
colors = []
vals = []

for row in cursor:
    if row[3] is None or row[0] in ['KGFK', 'KRAP']:
        continue
    lats.append(row[2])
    lons.append(row[1])
    vals.append(row[3])
    colors.append('#ff0000' if row[3] < 0 else '#00ff00')


m = MapPlot(sector='midwest', axisbg='white',
            title='NWS 1 Jul 2015 - 20 Jan 2016 Precipitation Departure [inches]',
            subtitle='20 January 2016 based on NWS issued CLI Reports')
m.plot_values(lons, lats, vals, fmt='%.1f', textsize=16, color=colors)
m.postprocess(filename='160121.png')
