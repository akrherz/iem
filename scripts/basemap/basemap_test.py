from mpl_toolkits.basemap import Basemap, cm
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import rgb2hex
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import pylab
import math
import Ngl
import iemplot
import iemdb
POSTGIS = iemdb.connect('postgis', bypass=True)
pcursor = POSTGIS.cursor()

fig = plt.figure(num=None, figsize=(11.3,7.00))
#fig = plt.figure(num=None, figsize=(6.15,4.1))
# Set the axes instance
ax = plt.axes([0,0,1,1], axisbg=(0.4471,0.6235,0.8117))

m = Basemap(projection='lcc', urcrnrlat=47.7, llcrnrlat=23.08, urcrnrlon=-62.5,
             llcrnrlon=-120, lon_0=-98.7, lat_0=39, lat_1=33, lat_2=45,
             resolution='l', ax=ax)
m.fillcontinents(color='0.7',zorder=0)

def clrbar(MAX):
        x=0
        ytics=[]

        while x<=MAX:
              ytics.append(x)
              x=x+1

        x=0
#               left,bottom,w,h
        ax2 = plt.axes([0.97,0.09,0.02,0.75], frameon=True, axisbg='w', yticks=ytics, xticks=[])
        for tick in ax2.yaxis.get_major_ticks():
            tick.label1.set_fontsize(10)
            tick.tick1On=False
            tick.tick2On=False

        while x<=MAX:
              c=rgb2hex(floatRgb(x,1,MAX))
              if x==0:
                 c='w'

              ax2.barh(x,1,align='center',height=1,color=c)
              x=x+1

        print MAX

        return


def floatRgb(mag, cmin, cmax):
       """
       Return a tuple of floats between 0 and 1 for the red, green and
       blue amplitudes.
       """

       try:
              # normalize to [0,1]
              x = float(mag-cmin)/float(cmax-cmin)
       except:
              # cmax = cmin
              x = 0.5
       blue = min((max((4*(0.75-x), 0.)), 1.))
       red  = min((max((4*(x-0.25), 0.)), 1.))
       green= min((max((4*math.fabs(x-0.5)-1., 0.)), 1.))
       return (red, green, blue)


# Load up shapefile
shp_info = m.readshapefile('/mesonet/data/gis/static/shape/4326/iowa/iacounties', 'c')

pcursor.execute("""
select ugc, count(*) from warnings 
WHERE substr(ugc,0,4) = 'IAC' and issue < '2011-01-01' and 
issue > '1995-01-01' and phenomena in ('SV','TO') and significance = 'W' 
GROUP by ugc ORDER by count DESC
""")
fipsdata = {}
colors = {}
maxV = 0
for row in pcursor:
    ugc = row[0] 
    cnt = float(row[1]) / 15.0
    fipsdata[ugc] = cnt
    if cnt > maxV:
        maxV = cnt


UGCS = []
for shapedict in m.c_info:
    ugc = "IAC%s" % (shapedict['CNTY_FIPS'],)
    UGCS.append( ugc )
    if fipsdata.get(ugc):
        mag=fipsdata[ugc]
        colors[ugc]=floatRgb(mag,1,maxV) # assign color to colors[fipsnumber]
        
    else:
        colors[ugc] = 'w' # assign white to colors[fipsnumber] not in file

for nshape,seg in enumerate(m.c):
    ugc = UGCS[nshape]
    color=rgb2hex(colors[ugc])
    poly=Polygon(seg,fc=color,ec='k',zorder=2, lw=.1)
    ax.add_patch(poly)

clrbar(maxV)
fig.savefig('test.png')