# Attempt to read and plot a postgis polygon, this would simplify things a lot
from mpl_toolkits.basemap import Basemap
import math
import iemplot
from osgeo import ogr
from shapely.wkb import loads
from numpy import asarray
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
from matplotlib.colors import rgb2hex
import Image

fig = plt.figure(num=None, figsize=(6.8,5.40))
ax = plt.axes([0,0,0.85,1], axisbg=(0.4471,0.6235,0.8117))  
map = Basemap(projection='lcc', urcrnrlat=47.7, llcrnrlat=23.08, urcrnrlon=-62.5,
             llcrnrlon=-120, lon_0=-98.7, lat_0=39, lat_1=33, lat_2=45,
             resolution='l')
map.fillcontinents(color='0.7',zorder=0)

shp_info = map.readshapefile('/mesonet/data/gis/static/shape/4326/us/states', 'st', drawbounds=True)


source = ogr.Open("PG:host=iemdb dbname=postgis user=nobody")
data = source.ExecuteSQL("""
--- select cwa.wfo, foo2.count, cwa.the_geom from cwa LEFT OUTER JOIN 
---   (SELECT wfo, count(*) from warnings_2011 WHERE gtype = 'P'
---   and phenomena = 'TO' and significance = 'W' GROUP by wfo) as foo ON (cwa.wfo = foo.wfo)
---   ORDER by foo.count DESC NULLS LAST
 select cwa.wfo, foo2.round as count,  cwa.the_geom from cwa LEFT OUTER JOIN
(select wfo, count(*), round(avg(count)::numeric,2) from (select phenomena, significance, eventid, wfo, extract(year from issue) as yr, count(*) from warnings where issue > '2007-10-01' and phenomena = 'TO' and significance = 'W' and gtype = 'C' GROUP by yr, phenomena, significance, eventid, wfo) as foo GROUP by wfo) as foo2 ON (cwa.wfo = foo2.wfo)
ORDER by foo2.count DESC NULLS LAST
""")

maxV = None
patches = []
while 1:
    feature = data.GetNextFeature()
    #print dir(feature)
    if not feature:
        break
    cnt = feature.GetField('count')
    if not maxV:
        maxV = int(cnt + 1.0)
    if cnt is None:
        c = 'w'
    else:
        c = iemplot.floatRgb(cnt,1,maxV)
        c = rgb2hex(c)
    geom = loads(feature.GetGeometryRef().ExportToWkb())
    for polygon in geom:
        a = asarray(polygon.exterior)
        x,y = map(a[:,0], a[:,1])
        a = zip(x,y)
        p = Polygon(a,fc=c,ec='k',zorder=2, lw=.1)
        patches.append(p)

          
ax.add_collection(PatchCollection(patches,match_original=True))
iemplot.bmap_clrbar(maxV+1)

#for nshape,seg in enumerate(map.st):
#    poly=Polygon(seg,fc='',ec='k',zorder=2, lw=.1)
#    ax.add_patch(poly)

# Top label
plt.text(0.5, 0.97, '1 Oct 2007 - 31 Aug 2011 Counties per Tornado Warning', transform=ax.transAxes,
    bbox=dict(boxstyle='square', facecolor='w', ec='b'), size=7,
    horizontalalignment='center', verticalalignment='center')

# Logo!
#logo = Image.open('../../htdocs/images/logo_small.png')
#ax3 = plt.axes([0.0,0.06,0.1,0.1], frameon=False, axisbg=(0.4471,0.6235,0.8117), yticks=[], xticks=[])
#ax3.imshow(logo, origin='lower')

#plt.text(0.08, 0.035,'Iowa State University', size='small', color='#222d7d',
#     horizontalalignment='center',
#     verticalalignment='center',
#     transform = ax.transAxes)

#plt.text(0.93, 0.37, 'Warnings issued by Office', transform=ax.transAxes,
#    size='small', color='k', horizontalalignment='left', rotation='vertical')

fig.savefig('test.png')
#import iemplot
#iemplot.makefeature('test')
