"""
  Plot on a basemap the path of a spotter network dude 
"""
from mpl_toolkits.basemap import Basemap, cm
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import mx.DateTime
import Image
import iemdb
POSTGIS = iemdb.connect('iem', bypass=True)
pcursor = POSTGIS.cursor()

fig = plt.figure(num=None, figsize=(11.3,7.00))
#fig = plt.figure(num=None, figsize=(6.15,4.1))
# Set the axes instance
ax = plt.axes([0.01,0,0.9,0.9], axisbg=(0.4471,0.6235,0.8117))
#m = Basemap(projection='lcc',
#            urcrnrlat=46.6, llcrnrlat=31.3, urcrnrlon=-87.5, llcrnrlon=-107.2, 
#             lon_0=-95.7, lat_0=40, lat_1=42, lat_2=44, resolution='i', ax=ax)
m = Basemap(projection='lcc', urcrnrlat=47.7, llcrnrlat=23.08, urcrnrlon=-62.5,
             llcrnrlon=-120, lon_0=-98.7, lat_0=39, lat_1=33, lat_2=45,
             resolution='l', ax=ax)

m.fillcontinents(color='0.7',zorder=0)
m.drawstates()
m.drawcountries()
colors = ['black', 'green', 'red', 'yellow', 'blue', 'orange', 'purple',
          'black', 'green', 'red', 'yellow', 'blue', 'orange', 'purple']
symbols = ['x', 'o', '^', 'x', 'o', '^','x', 'o', '^','x', 'o', '^','x', 'o', '^',
           'x', 'o', '^','x', 'o', '^',]

lats = []
lons = []
pcursor.execute("""
     select distinct x(geom), y(geom) from summary_2012 s JOIN stations t
     on (t.iemid  = s.iemid) where t.network ~* 'COOP' and s.max_tmpf >= 100
    """)
for row in pcursor:
    lats.append( row[1] )
    lons.append( row[0] )
    
xs, ys = m(lons, lats)
ax.scatter(xs, ys, marker='+', s=40, c='r')

ax.text(0.17, 1.06,"2012 NWS COOP 100+ Degree Temperature Reports (thru 3 July)",transform=ax.transAxes,
        horizontalalignment='left', verticalalignment='center')

#logo = Image.open('../../htdocs/images/logo_small.png')
#ax3 = plt.axes([0.15,0.90,0.1,0.1], frameon=False, 
#               axisbg=(0.4471,0.6235,0.8117), yticks=[], xticks=[])
#ax3.imshow(logo, origin='lower')

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')