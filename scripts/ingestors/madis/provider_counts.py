import netCDF3
import mx.DateTime
import sys

data = {}
runts = mx.DateTime.DateTime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]) )

fp = "/mnt/mesonet/data/madis/mesonet/%s00.nc" % (runts.strftime("%Y%m%d_%H"),)
ioc_nc = netCDF3.Dataset(fp, 'r')
sz = ioc_nc.variables["stationName"].shape[0]
for idx in range(sz):
  provider = ("".join(ioc_nc.variables["dataProvider"][idx])).strip()
  if not data.has_key(provider):
    data[provider] = {'ioc': 0, 'gsd': 0}
  data[provider]['ioc'] += 1

ioc_nc.close()

fp = "/mesonet/data/madis/mesonet/%s00.nc" % (runts.strftime("%Y%m%d_%H"),)
gsd_nc = netCDF3.Dataset(fp, 'r')
sz = gsd_nc.variables["stationName"].shape[0]
for idx in range(sz):
  provider = ("".join(gsd_nc.variables["dataProvider"][idx])).strip()
  if not data.has_key(provider):
    data[provider] = {'ioc': 0, 'gsd': 0}
  data[provider]['gsd'] += 1

gsd_nc.close()

ps = data.keys()
ps.sort()
print "Provider Report for: %s GMT" % (runts.strftime("%d %M %Y %H"),)
print "%-12s %10s %10s" % ("Provider", "IOC_COUNT", "GSD_COUNT")
for p in ps:
  print "%-12s %10i %10i" % (p, data[p]['ioc'], data[p]['gsd'])
