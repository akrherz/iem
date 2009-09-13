
import lib, mx.DateTime, numpy

nc = lib.load_netcdf( mx.DateTime.DateTime(1997,5,1) )

y = int( (42.03 - nc.variables['lat'][0]) * 100)
x = int( (-91.58 - nc.variables['lon'][0]) * 100)

a = nc.variables['precipitation'][:,y,x]
for i in range(31):
  print i, numpy.sum( a[(i*96):((i+1)*96)] ) / 25.4
print numpy.sum( a ) / 25.4
