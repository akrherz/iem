# Attempt to read and plot a postgis polygon, this would simplify things a lot
from mpl_toolkits.basemap import Basemap
from osgeo import ogr
from shapely.wkb import loads
from numpy import asarray
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt

fig = plt.figure(num=None, figsize=(11.3,7.00))
ax = plt.axes([0,0,1,1], axisbg=(0.4471,0.6235,0.8117))  
map = Basemap(projection='lcc', urcrnrlat=47.7, llcrnrlat=23.08, urcrnrlon=-62.5,
             llcrnrlon=-120, lon_0=-98.7, lat_0=39, lat_1=33, lat_2=45,
             resolution='l')
map.fillcontinents(color='0.7',zorder=0)

source = ogr.Open("PG:host=iemdb dbname=postgis user=nobody")
#data = source.ExecuteSQL("select geom from warnings_2011 where gtype = 'P' LIMIT 1")
data = source.ExecuteSQL("select the_geom from states where state_abbr = 'FL'")

patches = []
while 1:
    feature = data.GetNextFeature()
    if not feature:
        break
    geom = loads(feature.GetGeometryRef().ExportToWkb())
    for polygon in geom:
        a = asarray(polygon.exterior)
        x,y = map(a[:,0], a[:,1])
        a = zip(x,y)
        p = Polygon(a,fc='r',ec='k',zorder=2, lw=.1)
        patches.append(p)

          
ax.add_collection(PatchCollection(patches,match_original=True))

fig.savefig('test.png')