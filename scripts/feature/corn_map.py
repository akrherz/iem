import datetime
import numpy

data = {}
d2013 = {}

for linenum, line in enumerate(open('/home/akrherz/Downloads/CA8A1383-B422-399E-A91A-033FE9DE5312.csv')):
    if linenum == 0:
        continue
    tokens = line.split(",")
    day = datetime.datetime.strptime(tokens[3], '%Y-%m-%d')
    if day.month == 5 and day.day in range(1,8):
        state = tokens[5]
        val = float(tokens[-1])
        if not data.has_key(state):
            data[state] = []
        if day.year == 2013:
            d2013[state] = val
        else:
            data[state].append( val )

results = {}

for state in data.keys():
    ar = numpy.array(data[state])
    print "%s %.1f %.0f" % ( state, numpy.average(ar), d2013[state])
    results[ state ] = {'d2013': d2013[state], 'avg': numpy.average(ar)}
    
from mpl_toolkits.basemap import Basemap
from osgeo import ogr
from shapely.wkb import loads
from numpy import asarray
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
from matplotlib.colors import rgb2hex
import matplotlib.patheffects as PathEffects
from iem import constants

fig = plt.figure(num=None, figsize=(10.24,7.68))
ax = plt.axes([0.01,0,0.9,0.9], axisbg=(1,1,1))  
m = Basemap(projection='merc', fix_aspect=False,
                           urcrnrlat=constants.MW_NORTH,
                           llcrnrlat=constants.MW_SOUTH,
                           urcrnrlon=(constants.MW_EAST + 2.),
                           llcrnrlon=(constants.MW_WEST - 2.),
                           lat_0=45.,lon_0=-92.,lat_ts=42.,
                           resolution='i', ax=ax)
m.fillcontinents(color='tan',zorder=0)

source = ogr.Open("PG:host=iemdb dbname=postgis user=nobody")
#data = source.ExecuteSQL("select geom from warnings_2011 where gtype = 'P' LIMIT 1")
data = source.ExecuteSQL("""select the_geom, state_name,
ST_x(ST_Centroid(the_geom)) as x, ST_Y(ST_Centroid(the_geom)) as y from states""")

from iem import plot
maue = plot.maue(15)
bins = [1,2,3,4,5,7,10,15,20,25,30,35,40,50,75,100]

def get_color(val, minvalue, maxvalue):
    if val < bins[0]:
        return "None"
    for i in range(1,len(bins)):
        if val < bins[i]:
            return maue(i-1)
    return maue(14)

patches = []
while 1:
    feature = data.GetNextFeature()
    if not feature:
        break
    name = feature.GetField("state_name")
    if not results.has_key(name.upper()):
        continue
    geom = loads(feature.GetGeometryRef().ExportToWkb())
    c = get_color(results[name.upper()]['d2013'],0,100)
    for polygon in geom:
        a = asarray(polygon.exterior)
        x,y = m(a[:,0], a[:,1])
        a = zip(x,y)
        p = Polygon(a,fc=c,ec='k',zorder=2, lw=.1)
        patches.append(p)

    x,y = m(feature.GetField('x'), feature.GetField('y'))
    diff = results[name.upper()]['d2013'] - results[name.upper()]['avg']
    txt = ax.text(x,y, '%.0f\n%.0f' % (results[name.upper()]['d2013'],
                                       diff), 
                  verticalalignment='center', horizontalalignment='center', 
                  size=20, zorder=5)
    txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground="w")])

          
ax.add_collection(PatchCollection(patches,match_original=True))

axaa = plt.axes([0.92, 0.1, 0.07, 0.8], frameon=False,
                      yticks=[], xticks=[])
colors = []
for i in range(len(bins)):
    colors.append( rgb2hex(maue(i)) )
    txt = axaa.text(0.5, i, "%s" % (bins[i],), ha='center', va='center',
                          color='w')
    txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                     foreground="k")])
axaa.barh(numpy.arange(len(bins)), [1]*len(bins), height=1,
                color=maue(range(len(bins))),
                ec='None')

ax.text(0.17, 1.05, "5 May 2013 USDA Percentage of Corn Planted by State\nDeparture from 1979-2012 Average for First week of May", transform=ax.transAxes,
     size=14,
    horizontalalignment='left', verticalalignment='center')
# Logo!
import Image
logo = Image.open('../../htdocs/images/logo_small.png')
ax3 = plt.axes([0.05,0.9,0.1,0.1], frameon=False, axisbg=(0.4471,0.6235,0.8117), yticks=[], xticks=[])
ax3.imshow(logo)

fig.savefig('test.svg')