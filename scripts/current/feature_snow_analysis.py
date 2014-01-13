'''
 Generate an analysis of snowfall reports to be used for daily IEM Feature
'''

from pyiem.plot import MapPlot
import psycopg2
import numpy as np
from pyiem import iemre
import pandas as pd
import matplotlib.cm as cm
import iemplot

IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
icursor = IEM.cursor()
POSTGIS = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
pcursor = POSTGIS.cursor()

# Query COOP Data...
(COOP, LSR) = (1,2)
row_list = []
icursor.execute("""
    SELECT id, sum(snow), 
    ST_x(geom) as lon, 
    ST_y(geom) as lat, county, count(*) from
    summary t JOIN stations s ON (s.iemid = t.iemid) where 
    (network ~* 'COOP' or network ~* 'COCORAHS') and 
    day in ('2014-01-02', '2014-01-03') and snow >= 0 and 
    ST_x(geom) BETWEEN %s and %s and
    ST_y(geom) BETWEEN %s and %s  
    GROUP by id, lon, lat, county
""", (iemre.WEST, iemre.EAST, iemre.SOUTH, iemre.NORTH))
for row in icursor:
    #if row[2] < -93.6:
    #    continue
    if row[0] in ('ESTI4', 'CINI4', 'ALXI4'):
        print row
        continue
    row_list.append(dict(val=row[1], lat=row[3], lon=row[2], source=COOP))

# Query LSR Data...
pcursor.execute("""
    SELECT state, max(magnitude) as val, 
        ST_x(geom) as lon, 
       ST_y(geom) as lat
      from lsrs WHERE type in ('S') and magnitude > 0 and 
      valid > '2014-01-01 12:00' and valid < '2014-01-31 23:59'
      GROUP by state, lon, lat
""")
for row in pcursor:
    row_list.append(dict(val=row[1], lat=row[3], lon=row[2], source=LSR))

df = pd.DataFrame(row_list)
'''
 So, we are trying to do some QC here.  Some tenants
 1) We need more zeros to help the analysis have sharper cutoffs
 2) We'd like to favor COOP data over LSRs
'''

lats = []
lons = []
vals = []
data = np.ones( (iemre.NY, iemre.NX)) * -99
# Pass one, create our estimates
for i, lat in enumerate(iemre.YAXIS):
    for j, lon in enumerate(iemre.XAXIS):
        lon1 = lon + 0.5
        lat1 = lat + 0.5
        cell_df = df[ ((df['lat'] >= lat) & (df['lat'] < lat1) & 
                       (df['lon'] >= lon) & (df['lon'] < lon1))]
        if len(cell_df) > 0:
            data[i,j] = cell_df.max()['val']
# Pass two, check our neighbors
for i, lat in enumerate(iemre.YAXIS):
    for j, lon in enumerate(iemre.XAXIS):
        if i == 0 or j == 0 or i == (len(iemre.YAXIS)-1) or j == (len(iemre.XAXIS)-1):
            continue
        if data[i,j] < 0:
            continue
        neighbors = max(data[i-1,j], data[i+1,j], data[i,j-1], data[i,j+1])
        if neighbors < 0:
            lats.append( lat + 0.125 )
            lons.append( lon + 0.125 )
            vals.append( 0 )
            continue
        if data[i,j] > neighbors + 2.:
            print 'Bullseye i:%s j:%s val:%s' % (i,j, data[i,j])
            continue
        lats.append( lat + 0.125 )
        lons.append( lon + 0.125 )
        vals.append( data[i,j] )

clevs = np.array([0.01,0.1,0.25,0.5,1,2,3,5,7,9,11,13,15,17])

m = MapPlot(sector='iowa',
            title="1 Jan 2013 - IEM Snowfall Total Analysis",
            subtitle="Snowfall totals up until 8 AM 1 Jan 2014")
xs,ys = np.meshgrid( np.concatenate([iemre.XAXIS, [iemre.XAXIS[-1] + 0.25,]]),
                     np.concatenate([iemre.YAXIS, [iemre.YAXIS[-1] + 0.25,]]))
cmap = cm.get_cmap('Spectral_r')
cmap.set_over('black')
cmap.set_under('white')
m.contourf(lons, lats, vals, clevs, cmap=cmap)
#m.plot_values(lons, lats, vals, '%.1f')
m.drawcounties()
m.postprocess(filename='test.ps')
iemplot.makefeature('test')
