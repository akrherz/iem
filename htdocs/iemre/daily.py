#!/mesonet/python/bin/python

import sys
sys.path.insert(0, "../../scripts/iemre/")
import os
import cgi
import constants
import netCDF3
import mx.DateTime
import simplejson

form = cgi.FormContent()
ts = mx.DateTime.strptime( form["date"][0], "%Y-%m-%d")
lat = float( form["lat"][0] )
lon = float( form["lon"][0] )
format = form["format"][0]

i,j = constants.find_ij(lon, lat)
offset = int((ts - (ts + mx.DateTime.RelativeDateTime(month=1,day=1))).days)

res = {'data': [], }

fp = "/mnt/mesonet/data/iemre/%s_daily.nc" % (ts.year,)
if os.path.isfile(fp):
  nc = netCDF3.Dataset("/mnt/mesonet/data/iemre/%s_daily.nc" % (ts.year,), 'r')

  c2000 = ts + mx.DateTime.RelativeDateTime(year=2000)
  coffset = int((c2000 - (mx.DateTime.DateTime(2000,1,1))).days)
  cnc = netCDF3.Dataset("/mnt/mesonet/data/iemre/dailyc.nc", 'r')

  res['data'].append({
    'daily_high_f': "%.1f" % (
       constants.k2f(nc.variables['high_tmpk'][offset,j,i]),),
    'climate_daily_high_f': "%.1f" % (
       constants.k2f(cnc.variables['high_tmpk'][coffset,j,i]),),
    'daily_low_f': "%.1f" % (
       constants.k2f(nc.variables['low_tmpk'][offset,j,i]),),
    'climate_daily_low_f': "%.1f" % (
       constants.k2f(cnc.variables['low_tmpk'][coffset,j,i]),),
    'daily_precip_in': "%.2f" % (
       nc.variables['p01d'][offset,j,i] / 25.4,),
    'climate_daily_precip_in': "%.2f" % (
       cnc.variables['p01d'][coffset,j,i] / 25.4,),
  })
  nc.close()
  cnc.close()

print 'Content-type: text/plain\n'
print simplejson.dumps( res )
