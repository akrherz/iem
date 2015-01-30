from mpl_toolkits.basemap import Basemap
from osgeo import ogr
from shapely.wkb import loads
from numpy import asarray
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
from iem import constants
import matplotlib.patheffects as PathEffects

fig = plt.figure(num=None, figsize=(6,5))
ax = plt.axes([0,0,1,1], axisbg=(0.4471,0.6235,0.8117))  
m = Basemap(projection='merc', fix_aspect=False,
                           urcrnrlat=constants.IA_NORTH, 
                           llcrnrlat=constants.IA_SOUTH, 
                           urcrnrlon=constants.IA_EAST, 
                           llcrnrlon=constants.IA_WEST, 
                           lat_0=45.,lon_0=-92.,lat_ts=42.,
                           resolution='i')
m.fillcontinents(color='0.7',zorder=0)
m.drawstates(2.)
source = ogr.Open("PG:host=iemdb dbname=postgis user=nobody")
data = source.ExecuteSQL("""select geom, phenomena, significance, gtype from warnings_2013 
  where 
 wfo in ('DMX','DVN','ARX','FSD','OAX') and issue < '2013-04-09 18:00' and
 expire > '2013-04-09 18:00'""")

fill_colors = {'SV.W': 'None', 'SV.A': 'yellow', 'FA.A': 'green' ,
               'WS.W': 'purple', 'WS.A': 'pink', 'WW.Y': 'pink'}
edge_colors = {'SV.W': 'yellow' , 'FL.W': 'green'}
zorder = {'SV.W': 4, 'FL.W': 4, 'WS.A': 3}
linewidth = {'SV.W': 2}

patches = []
patches2 = []
uniq = []
while 1:
    feature = data.GetNextFeature()
    if not feature:
        break
    phenomena = feature.GetField('phenomena')
    significance = feature.GetField('significance')
    gtype = feature.GetField('gtype')
    lookup = '%s.%s' % (phenomena, significance)
    if lookup not in uniq:
        print lookup, gtype
        uniq.append( lookup )
    if gtype == 'C' and phenomena in ('SV', 'TO') and significance == 'W':
        continue
    geom = loads(feature.GetGeometryRef().ExportToWkb())
    for polygon in geom:
        a = asarray(polygon.exterior)
        x,y = m(a[:,0], a[:,1])
        a = zip(x,y)
        p = Polygon(a,fc=fill_colors.get(lookup, 'None'),
                      ec=edge_colors.get(lookup, 'k'),
                      zorder=zorder.get(lookup, 2), 
                      lw=linewidth.get(lookup, .1) )
        if gtype == 'P':
            patches2.append(p)
        else:
            patches.append(p)

          
ax.add_collection(PatchCollection(patches,match_original=True))
ax.add_collection(PatchCollection(patches2,match_original=True))

import iemdb
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()
icursor.execute("""
select id, avg(tmpf), x(geom), y(geom) from current_log c JOIn stations s 
 on (s.iemid = c.iemid) WHERE s.network in ('AWOS','IA_ASOS') and 
 valid between '2013-04-09 17:50' and '2013-04-09 18:00' 
 and id not in ('MPZ') GROUP by id, x, y
""")
for row in icursor:
    x,y = m(row[2], row[3])
    txt = ax.text(x,y, '%.0f' % (row[1],), color='white', size=18)
    #txt.set_path_effects([PathEffects.withStroke(linewidth=2,
    #                                             foreground="black")])

txt = ax.text(0.25, 0.05, "Valid: 6 PM 9 April 2013", transform=ax.transAxes, 
              size=20, va='top', color='black' )
#txt.set_path_effects([PathEffects.withStroke(linewidth=2,
#                                                 foreground="black")])

txt = ax.text(0.05, 0.1, "Severe T'Storm\nWatch", transform=ax.transAxes, 
              size=15, va='top', color='black' )
#txt.set_path_effects([PathEffects.withStroke(linewidth=2,
#                                                 foreground="black")])

txt = ax.text(0.02, 0.95, "Ice Storm\nWarning", transform=ax.transAxes, 
              size=15, va='top', color='white' )
#txt.set_path_effects([PathEffects.withStroke(linewidth=2,
#                                                 foreground="black")])

txt = ax.text(0.85, 0.9, "Flood\nWatch", transform=ax.transAxes, 
              size=15, va='top', color='white' )
#txt.set_path_effects([PathEffects.withStroke(linewidth=2,
#                                                 foreground="black")])

txt = ax.text(0.25, 0.8, "Severe T'Storm\nWarning", transform=ax.transAxes, 
              size=15, va='top', color='yellow' )
#txt.set_path_effects([PathEffects.withStroke(linewidth=2,
#                                                 foreground="black")])


fig.savefig('130410_s.svg')
#import iemplot
#iemplot.makefeature('test')