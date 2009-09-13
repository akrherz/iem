
import lib, mx.DateTime, numpy, pg, math

ts = mx.DateTime.DateTime(1997,5,1)
coop = pg.connect('coop', 'iemdb', user='nobody')
mesosite = pg.connect('mesosite', 'iemdb', user='nobody')

# Dict of station locations
locs = {}
rs = mesosite.query("SELECT x(geom) as lon, y(geom) as lat, name, id from stations WHERE network = 'IACLIMATE'").dictresult()
for i in range(len(rs)):
  locs[ rs[i]['id'] ] = rs[i]

obs = {}
rs = coop.query("SELECT stationid, sum(precip) as rain from alldata WHERE year = %s and month = %s GROUP by stationid" % (ts.year, ts.month) ).dictresult()

nc = lib.load_netcdf( ts )
precip = nc.variables['precipitation']
(tmsz, ysz, xsz) = numpy.shape( precip )

adjustment = numpy.zeros( ( ysz, xsz ), 'f')
adjustment[:,:] = 1.0

# Create a form to apply to the bias and then assign into the adjustment
siteform = numpy.zeros( (30,30), 'f')
for x in range(30):
  for y in range(30):
    siteform[x,y] = 1.0 - math.sqrt(math.pow(abs(x-15)/22.0,2) + math.pow(abs(y-15)/22.0,2) )

errors = []
for i in range(len(rs)):
  if not locs.has_key( rs[i]['stationid'].upper() ):
    continue
  lat = locs[ rs[i]['stationid'].upper() ]['lat']
  lon = locs[ rs[i]['stationid'].upper() ]['lon']
  x,y = lib.nc_lalo2pt(nc, lat, lon)
  obs = rs[i]['rain']
  analysis = numpy.sum( precip[:,y,x] ) / 25.4
  errors.append(  analysis - obs   )
  # Figure out the adjustment ratio
  ratio = obs / analysis
  if x < 15:
    x = 15
  if x > (xsz-15):
    x = xsz-15
  if y < 15:
    y = 15
  if y > (ysz-15):
    y = ysz-15
  adjustment[y-15:y+15, x-15:x+15] = 1.0 + ((ratio - 1.0) * siteform )

#for t in range(tmsz):
#  precip[t,:,:] = precip[t,:,:] * adjustment

print "BIAS", sum(errors) / float(len(errors))

nc.close()
