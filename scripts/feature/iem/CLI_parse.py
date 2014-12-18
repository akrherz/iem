import iemdb
IEM = iemdb.connect('iem', bypass=True)
cursor = IEM.cursor()



cursor.execute("""select station, st_x(geom), st_y(geom), snow_jul1 - snow_jul1_normal from cli_data c JOIN stations s on (s.id = c.station) WHERE s.network = 'NWSCLI' and c.valid = '2014-12-17' """)

lats = []
lons = []
vals = []

for row in cursor:
    if row[3] is None:
        continue
    lats.append(row[2])
    lons.append(row[1])
    vals.append(row[3])
        
from pyiem.plot import MapPlot

m = MapPlot(sector='midwest', axisbg='white',
       title='NWS 1 July - 17 December Snowfall Departure',
       subtitle= '17 December 2014 based on NWS issued CLI Reports')
m.plot_values(lons, lats, vals, fmt='%.1f', textsize=16)
m.postprocess(filename='test.ps')
import iemplot
iemplot.makefeature('test')
