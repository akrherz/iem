"""
Create a netCDF file of goes imagery?
"""
import pyproj
import netCDF4
import numpy

nc = netCDF4.Dataset("goes_west_latlon.nc", 'w')
nc.createDimension('x', 4400)
nc.createDimension('y', 5120)

lat = nc.createVariable('lat',numpy.float32, ('y', 'x') )
lat.long_name = 'Latitude'
lat.units = 'Degrees North'

lon = nc.createVariable('lon', numpy.float32, ('y', 'x'))
lon.long_name = 'Longitude'
lon.units = 'Degrees East'

p1 = pyproj.Proj(proj='lcc', lat_0=25, lat_1=25, lat_2=25, lon_0=-95, a=6371200.0, b=6371200.0)
p2 = pyproj.Proj(init='epsg:4326')

ll_x = -4226066.376
ll_y = -832192.755
dx = 1015.9
dy = 1015.9

lats = numpy.zeros( (5120,4400), numpy.float32)
lons = numpy.zeros( (5120,4400), numpy.float32)

for i in range(4400):
    if i % 100 == 0:
        print i
    for j in range(5120):
        x = ll_x + (i*dx)
        y = ll_y + (j*dy)
        x2, y2 = pyproj.transform(p1,p2, x,y)
        lats[j,i] = y2
        lons[j,i] = x2

lat[:] = lats[:]
lon[:] = lons[:]
nc.close()