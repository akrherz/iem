'''
 Create an analysis map for my own uses that shows the map differences
 between different postgres simplifies operations
'''
from mpl_toolkits.basemap import Basemap
from osgeo import ogr
from shapely.wkb import loads
from numpy import asarray
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
import sys
import psycopg2
POSTGIS = psycopg2.connect(database='postgis', host='iemdb')
cursor = POSTGIS.cursor()

UGC = sys.argv[1]

cursor.execute("""
 WITH e as (select ST_Extent(geom) as v, max(name) from nws_ugc where ugc = %s)
 
 SELECT ST_xmin(e.v) - 0.15, ST_xmax(e.v) + 0.15, 
 ST_ymin(e.v) - 0.15, ST_ymax(e.v) + 0.15, max from e
""", (UGC,))
row = cursor.fetchone()
xmin, xmax, ymin, ymax, ugcname = row

(fig, axes) = plt.subplots(2,3)

geoms = [ "ST_Simplify(ST_Buffer(ST_Buffer(\ngeom, -0.01),0.01),0.0025)",
         "ST_Simplify(ST_Buffer(ST_Buffer(\ngeom, -0.001),0.001),0.00025)",
         "geom", "ST_Simplify(geom,0.1)", "ST_Simplify(geom,0.01)"
         , "ST_Simplify(geom,0.001)"]

for row in range(2):
    for col in range(3):
        ax = axes[row,col]
        m = Basemap(projection='lcc', 
            urcrnrlat=ymax, llcrnrlat=ymin, 
            urcrnrlon=xmax, llcrnrlon=xmin, 
            lon_0=(xmax+xmin)/2., 
        lat_0=(ymax+ymin)/2.-5, lat_1=(ymax+ymin)/2., lat_2=(ymax+ymin)/2.+5,
        resolution='l', fix_aspect=True, ax=ax)
        #m.fillcontinents(color='b',zorder=0)
        m.set_axes_limits(ax=ax)
        g = geoms.pop()
        source = ogr.Open("PG:host=iemdb dbname=postgis")
        data = source.ExecuteSQL("select %s from nws_ugc where ugc = '%s'" % (g,
                                                                        UGC))

        patches = []
        while 1:
            feature = data.GetNextFeature()
            if not feature:
                break
            bindata = feature.GetGeometryRef().ExportToWkb()
            geom = loads(bindata)
            for polygon in geom:
                a = asarray(polygon.exterior)
                x,y = m(a[:,0], a[:,1])
                a = zip(x,y)
                p = Polygon(a,fc='r',ec='k',zorder=2, lw=.5)
                patches.append(p)

        ax.set_title(g, fontsize=8)
        ax.set_xlabel("Geometry size: %.3f KB" % (sys.getsizeof(bindata) / 1024.,),
                      fontsize=8)
        ax.add_collection(PatchCollection(patches,match_original=True))

#fig.suptitle("NWS UGC: %s Name: %s" % (UGC, ugcname))
fig.tight_layout()
fig.savefig('test.png')