import sys
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import pygrib
import numpy as np
from pyiem.datatypes import temperature
grbs = pygrib.open('rtma.t23z.awp2p5f000.grib2')

for grb in grbs:
    print grb.name
#    print np.shape( grb.values )
#    print grb.projparams
    
g = grbs.select(name='2 metre temperature')[0]
print dir(g), g['gridType']
print g['latitudeOfFirstGridPointInDegrees']
print g['longitudeOfFirstGridPointInDegrees']
print g['Nx']
print g['Ny']
print g['DxInMetres']
print g['DyInMetres']
lats, lons = g.latlons()
data = temperature(g['values'], 'K').value('F')
llcrnrlon = lons[0,0]
llcrnrlat = lats[0,0]
urcrnrlon = lons[-1,-1]
urcrnrlat = lats[-1,-1]
rsphere = (g.projparams['a'],g.projparams['b'])
lat_1 = g.projparams['lat_1']
lat_2 = g.projparams['lat_2']
lon_0 = g.projparams['lon_0']
projection = g.projparams['proj']
fig=plt.figure()
sys.stdout.write(repr(g.projparams)+'\n')
ax = fig.add_axes([0.1,0.1,0.75,0.75])
#m = Basemap(llcrnrlon=llcrnrlon,llcrnrlat=llcrnrlat,
#            urcrnrlon=urcrnrlon,urcrnrlat=urcrnrlat,rsphere=rsphere,lon_0=lon_0,
m = Basemap(llcrnrlon=-100,llcrnrlat=38,
            urcrnrlon=-86,urcrnrlat=46,rsphere=rsphere,lon_0=lon_0,
            lat_1=lat_1,lat_2=lat_2,resolution='l',projection=projection,area_thresh=10000)
x,y = m(lons, lats)
cs = m.contourf(x,y,data,20,cmap=plt.cm.jet)
m.drawcoastlines()
m.drawstates()
m.drawcountries()
# new axis for colorbar.
cax = plt.axes([0.875, 0.15, 0.03, 0.65])
plt.colorbar(cs, cax, format='%g') # draw colorbar
plt.axes(ax)  # make the original axes current again
plt.title('NDFD Temp CONUS %d-h forecast'% g['forecastTime'],fontsize=12)
plt.savefig('test.png')