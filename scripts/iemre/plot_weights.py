"""Diagnostic check of the climdiv_weights.nc file"""
import netCDF4
from pyiem.plot import MapPlot
import numpy
from pyiem import iemre

nc = netCDF4.Dataset("/mesonet/data/iemre/climdiv_weights.nc")
lons = nc.variables['lon'][:]
lons = numpy.append(lons, iemre.EAST)
lats = nc.variables['lat'][:]
lats = numpy.append(lats, iemre.NORTH)

m = MapPlot(sector='midwest')
x, y = numpy.meshgrid(lons, lats)
m.map.pcolormesh(x[:, :], y[:, :], nc.variables['IAC001'][:, :], latlon=True)
#           numpy.linspace(0,1,20))

# x = [iemre.WEST, iemre.WEST, iemre.EAST, iemre.EAST, iemre.WEST]
# y = [iemre.SOUTH, iemre.NORTH, iemre.NORTH, iemre.SOUTH, iemre.SOUTH]
# x, y = m.map(x, y)
# m.ax.plot(x, y, lw=3, color='r', zorder=5)

m.postprocess(filename='test.png')
