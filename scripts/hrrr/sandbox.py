import pygrib
import numpy as np
from scipy.interpolate import interp2d
import sys
import pyproj
 
llx = -96.7
lly = 40.37
urx = 90.1
ury = 43.61
 
grbs = pygrib.open('hrrr.2d.201307091200f000.grib2')

g = grbs.select(parameterName='Convective available potential energy',
                topLevel=0)[0]

cape = g['values']
lats, lons = g.latlons()

data = cape[ (lats > lly) & (lats < ury) & (lons > llx) & (lons < urx) ]
print np.average(data), np.shape(data)
sys.exit()




#f = interp2d(lons[miny:maxy,minx:maxx], lats[miny:maxy,minx:maxx], 
#             cape[miny:maxy,minx:maxx])
#print 'Out'
#sys.exit()

y = np.arange(-105, -90, 0.25)
x = np.arange(38, 50, 0.25)

print np.shape(cape), g['Nx'], g['Ny']

#data = f(x,y)
sys.exit()
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

ax.imshow(cape)

fig.savefig('test.png')

""" Remap to Iowa

dx = g['DxInMetres']
dy = g['DyInMetres']

LCC = pyproj.Proj(g.projparams)
x0, y0 = LCC( g['longitudeOfFirstGridPointInDegrees'], 
              g['latitudeOfFirstGridPointInDegrees'] )
xaxis = x0 + g['DxInMetres'] * np.arange( g['Nx'] )
yaxis = y0 + g['DyInMetres'] * np.arange( g['Ny'] )

x = []
y = []
for bx in [llx, urx]:
    for by in [lly, ury]:
        gx, gy = LCC(bx, by)
        x.append( np.digitize([gx,], xaxis)[0] )
        y.append( np.digitize([gy,], yaxis)[0] )
        
minx = min(x)
maxx = max(x)
miny = min(y)
maxy = max(y)

 """