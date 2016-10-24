import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from mpl_toolkits.basemap import Basemap
from pyiem.plot import MapPlot
from shapely.wkb import loads
import psycopg2
import numpy as np
DBCONN = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
cursor = DBCONN.cursor()
"""
(fig, ax) = plt.subplots(1,1)

m = MapPlot(title="27 January 2014 :: Terra MODIS True Color",
            subtitle="Orange Roads are those with 'Travel Not Recommended' Status (26-27 Jan), Red box (Blizzard Warning)")

x,y= m.map(-99.40,38.775)
x2,y2=m.map(-88.132,45.15)

img=mpimg.imread('/tmp/AERONET_Ames.jpg')
m.ax.imshow(img, extent=(x,x2,y, y2) )

cursor.execute('''select ST_asEWKB(ST_Transform(simple_geom,4326)) from roads_base
 WHERE segid in (select distinct segid from roads_2014_log where cond_code = 51 and valid > '2014-01-26')''')
for row in cursor:
    if row[0] is None:
        continue
    line = loads( str(row[0]) )
    for geo in line.geoms:
        (lons, lats) = geo.xy
        x,y = m.map(lons, lats)
        m.ax.plot(x,y, color='orange', lw=2)

cursor.execute('''
SELECT ST_asEWKB(ST_Buffer(ST_Collect(geom),0)) from warnings_2014 where phenomena = 'BZ'
and significance = 'W' and issue > '2014-01-26' and wfo in ('DMX','DVN', 'ARX') and substr(ugc, 1,2) = 'IA'
''')
row = cursor.fetchone()
geom = loads(str(row[0]))
a = np.asarray(geom.exterior)
x,y = m.map(a[:,0], a[:,1])
m.ax.plot(x,y, color='red', lw=2.5, zorder=2)

"""
(fig, ax) = plt.subplots(2, 1)

m = Basemap(projection='cea', llcrnrlat=40, urcrnrlat=44,
            llcrnrlon=-99, urcrnrlon=-89, resolution='i',
            ax=ax[0], fix_aspect=False)
m2 = Basemap(projection='cea', llcrnrlat=40, urcrnrlat=44,
             llcrnrlon=-99, urcrnrlon=-89, resolution='i',
             ax=ax[1], fix_aspect=False)

x, y = m(-99.4023, 38.7753)
x2, y2 = m(-88.1321, 45.2504)

img = mpimg.imread('aug22.jpg')
ax[0].imshow(img, extent=(x, x2, y, y2))
ax[0].set_title("22 August 2016 :: Terra MODIS True Color")

img = mpimg.imread('oct23.jpg')
ax[1].imshow(img, extent=(x, x2, y, y2))
ax[1].set_title("23 October 2016 :: Aqua MODIS True Color")

m.drawstates(linewidth=2.5)
m2.drawstates(linewidth=2.5)
plt.savefig('test.png')

"""
(fig, ax) = plt.subplots(1,1)

m = Basemap(projection='cea',llcrnrlat=40,urcrnrlat=44,
            llcrnrlon=-97,urcrnrlon=-90,resolution='i',
            ax=ax, fix_aspect=False)

x,y= m(-99.4023, 38.8753)
x2,y2=m(-88.1321, 45.3504)

img=mpimg.imread('ames.jpg')
ax.imshow(img, extent=(x,x2,y, y2) )
ax.set_title("2 January 2016 :: Terra MODIS True Color")

m.drawstates(linewidth=2.5)
plt.savefig('test.png')
"""
