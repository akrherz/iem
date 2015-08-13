import psycopg2
from pyiem.plot import MapPlot
IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
cursor = IEM.cursor()

cursor.execute("""select station, st_x(geom), st_y(geom),
    precip_jun1 - precip_jun1_normal from
    cli_data c JOIN stations s on (s.id = c.station)
    WHERE s.network = 'NWSCLI' and c.valid = '2015-08-12' """)

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
            title='NWS 1 June - 12 August Precipitation Departure [inches]',
            subtitle='12 August 2015 based on NWS issued CLI Reports')
m.plot_values(lons, lats, vals, fmt='%.2f', textsize=16, color=colors)
m.postprocess(filename='150813.png')
