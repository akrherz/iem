import psycopg2
import numpy as np
from pyiem.plot import MapPlot

SMOS = psycopg2.connect(database='smos', host='iemdb', user='nobody')
cursor = SMOS.cursor()

cursor.execute("""
select idx, ST_x(geom), ST_y(geom) from grid ORDER by idx
""")

idx = []
lats = []
lons = []
for row in cursor:
    idx.append( row[0] )
    lons.append( row[1] )
    lats.append( row[2] )
    
idx = np.array(idx)
lons = np.array(lons)
lats = np.array(lats)
m = MapPlot(sector='midwest')
x, y = m.map(lons, lats)
m.map.hexbin(x, y, C=idx)
#m.plot_values(lons,lats, idx, '%s',textsize=6)
m.postprocess(view=True)