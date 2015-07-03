import datetime
import numpy

data = {}
d2015 = {}

for linenum, line in enumerate(open('corn.csv')):
    if linenum == 0:
        continue
    tokens = line.replace('"','').split(",")
    day = datetime.datetime.strptime(tokens[3], '%Y-%m-%d')
    if day.month == 6 and day.day in range(23, 31):
        state = tokens[5]
        val = float(tokens[20])
        if not data.has_key(state):
            data[state] = []
        if day.year == 2015:
            d2015[state] = min([val, 99.99999])
        else:
            data[state].append( val )

results = {}
print data['IOWA']

for state in data.keys():
    ar = numpy.array(data[state])
    print "%s %.1f %.0f" % ( state, numpy.average(ar), d2015[state])
    results[ state ] = {'d2015': d2015[state], 'avg': numpy.average(ar)}
    
from mpl_toolkits.basemap import Basemap
from osgeo import ogr
from shapely.wkb import loads
from numpy import asarray
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
from matplotlib.colors import rgb2hex
import matplotlib.patheffects as PathEffects
from pyiem import iemre

fig = plt.figure(num=None, figsize=(10.24,7.68))
ax = plt.axes([0.01,0,0.9,0.9], axisbg=(1,1,1))  
m = Basemap(projection='merc', fix_aspect=False,
                           urcrnrlat=iemre.NORTH,
                           llcrnrlat=iemre.SOUTH,
                           urcrnrlon=(iemre.EAST),
                           llcrnrlon=(iemre.WEST),
                           lat_0=45.,lon_0=-92.,lat_ts=42.,
                           resolution='i', ax=ax)
m.fillcontinents(color='tan',zorder=0)

source = ogr.Open("PG:host=iemdb dbname=postgis user=nobody")
#data = source.ExecuteSQL("select geom from warnings_2011 where gtype = 'P' LIMIT 1")
data = source.ExecuteSQL("""select ST_Simplify(the_geom, 0.01), state_name,
ST_x(ST_Centroid(the_geom)) as x, ST_Y(ST_Centroid(the_geom)) as y from states""")

from pyiem.plot import maue
import matplotlib.colors as mpcolors
cmap = plt.get_cmap('jet')
cmap.set_over('white')
bins = range(0,101,10)

norm = mpcolors.BoundaryNorm(bins, cmap.N)

patches = []
while 1:
    feature = data.GetNextFeature()
    if not feature:
        break
    name = feature.GetField("state_name")
    if not results.has_key(name.upper()):
        continue
    geom = loads(feature.GetGeometryRef().ExportToWkb())
    c = cmap(norm([results[name.upper()]['d2015'],]))[0]
    for polygon in geom:
        a = asarray(polygon.exterior)
        x,y = m(a[:,0], a[:,1])
        a = zip(x,y)
        p = Polygon(a,fc=c,ec='k',zorder=2, lw=1)
        patches.append(p)

    x,y = m(feature.GetField('x'), feature.GetField('y'))
    diff = results[name.upper()]['d2015'] - results[name.upper()]['avg']
    txt = ax.text(x,y, '%.0f%%\n%s%.0f' % (results[name.upper()]['d2015'],
                                           '+' if diff > 0 else '', diff),
                  verticalalignment='center', horizontalalignment='center', 
                  size=20, zorder=5)
    txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground="w")])

          
ax.add_collection(PatchCollection(patches,match_original=True))

axaa = plt.axes([0.92, 0.1, 0.07, 0.8], frameon=False,
                      yticks=[], xticks=[])
colors = []
for i in range(len(bins)):
    colors.append( rgb2hex(cmap(i)) )
    txt = axaa.text(0.5, i, "%s" % (bins[i],), ha='center', va='center',
                          color='w')
    txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                     foreground="k")])
axaa.barh(numpy.arange(len(bins)), [1]*len(bins), height=1,
                color=cmap(norm(bins)),
                ec='None')

ax.text(0.17, 1.05, "28 June 2015 USDA Percentage of Soybean Acres Planted\nPercentage Points Departure from 1980-2014 Average for 23-30 June", transform=ax.transAxes,
     size=14,
    horizontalalignment='left', verticalalignment='center')
# Logo!
from PIL import Image
logo = Image.open('../../../htdocs/images/logo_small.png')
ax3 = plt.axes([0.05,0.9,0.1,0.1], frameon=False, axisbg=(0.4471,0.6235,0.8117), yticks=[], xticks=[])
ax3.imshow(logo)

fig.savefig('test.png')
