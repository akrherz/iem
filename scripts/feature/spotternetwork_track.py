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
POSTGIS = iemdb.connect('postgis', bypass=True)
pcursor = POSTGIS.cursor()

fig = plt.figure(num=None, figsize=(11.3,7.00))
#fig = plt.figure(num=None, figsize=(6.15,4.1))
# Set the axes instance
ax = plt.axes([0.01,0,0.9,0.9], axisbg=(0.4471,0.6235,0.8117))
m = Basemap(projection='lcc',
            urcrnrlat=46.6, llcrnrlat=31.3, urcrnrlon=-87.5, llcrnrlon=-107.2, 
             lon_0=-95.7, lat_0=40, lat_1=42, lat_2=44, resolution='i', ax=ax)
m.fillcontinents(color='0.7',zorder=0)
m.drawstates()
colors = ['black', 'green', 'red', 'yellow', 'blue', 'orange', 'purple',
          'black', 'green', 'red', 'yellow', 'blue', 'orange', 'purple']
symbols = ['x', 'o', '^', 'x', 'o', '^','x', 'o', '^','x', 'o', '^','x', 'o', '^',
           'x', 'o', '^','x', 'o', '^',]
sts = mx.DateTime.DateTime(2012,5,1)
ets = mx.DateTime.DateTime(2012,5,28)
now = sts
while now < ets:
    lats = []
    lons = []
    pcursor.execute("""
     select x(geom), y(geom) from spotternetwork_2012 where name = 'Mike Bettes'
     and valid BETWEEN '%s 07:00'::timestamp 
         and '%s 07:00'::timestamp + '24 hours'::interval ORDER by valid ASC
    """ %(now.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")))
    for row in pcursor:
        if len(lats) > 0:
            dist = ((row[1] - lats[-1])**2 + (row[0] - lons[-1])**2) **0.5
            if dist > 4:
                print 'BAD', dist, len(lats), now
                continue
        lats.append( row[1] )
        lons.append( row[0] )
    
    if len(lats) > 10:
        xs, ys = m(lons, lats)
        ax.plot(xs, ys, label=now.strftime("%-m/%d"), marker=symbols.pop(),
                c=colors.pop(),markevery=60)
    now += mx.DateTime.RelativeDateTime(days=1)

ax.legend(loc=3)
ax.text(0.17, 1.06,"Weather Channel Great Tornado Hunt 1-27 May 2012\nChase vehicle location as reported via spotternetwork\nDates are split at 7 AM",transform=ax.transAxes,
        horizontalalignment='left', verticalalignment='center')

#logo = Image.open('../../htdocs/images/logo_small.png')
#ax3 = plt.axes([0.15,0.90,0.1,0.1], frameon=False, 
#               axisbg=(0.4471,0.6235,0.8117), yticks=[], xticks=[])
#ax3.imshow(logo, origin='lower')

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')