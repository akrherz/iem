from pyiem.plot import MapPlot, mask_outside_polygon
from shapely.wkb import loads
from descartes.patch import PolygonPatch
from shapely.geometry import Polygon
import psycopg2
import numpy as np
DBCONN = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
cursor = DBCONN.cursor()

cursor.execute("""SELECT ST_asEWKB(
            ST_Transform(
                ST_Simplify(
                    ST_Union(ST_Transform(the_geom,2163)),
                    500.),
                4326)) from states 
        WHERE state_abbr = 'IA'
---    where state_abbr in ('MI','WI', 'IL', 'IN', 'OH', 'KY', 'MO', 'KS',
---    'NE', 'SD', 'ND', 'MN', 'IA')
 """)

m = MapPlot('iowa')
lons = np.linspace(-110,-70,50)
lats = np.linspace(28,52,50)
vals = np.linspace(0,50,50)
m.contourf(lons,lats,vals, vals)

#"""
for row in cursor:
    multipoly = loads( str(row[0]) )
    for geo in multipoly.geoms:
        if geo.area < 1:
            continue
        (lons,lats) = geo.exterior.xy
        print 'Masking with geo...', geo.area, len(lons)

        ar = zip(lons, lats)
        ar.reverse()
        np.save('iowa_ccw.npy', ar)
        #mask_outside_polygon(ar, ax=m.ax)
        #poly = PolygonPatch(Polygon(zip(x,y)), fc='r', zorder=10000)
        #m.ax.add_patch(poly)
#""" 
m.postprocess(filename='test.png')