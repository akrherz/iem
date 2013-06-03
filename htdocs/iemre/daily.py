#!/usr/bin/env python

import sys
import os
import cgi
from pyiem import iemre, datatypes
import netCDF4
import datetime
import json

form = cgi.FormContent()
ts = datetime.datetime.strptime( form["date"][0], "%Y-%m-%d")
lat = float( form["lat"][0] )
lon = float( form["lon"][0] )
fmt = form["format"][0]

i,j = iemre.find_ij(lon, lat)
offset = iemre.daily_offset(ts)

res = {'data': [], }

fn = "/mesonet/data/iemre/%s_mw_daily.nc" % (ts.year,)

sys.stdout.write('Content-type: text/plain\n\n')
if not os.path.isfile(fn):
    sys.stdout.write( json.dumps( res ) )
    sys.exit()

if i is None or j is None:
    sys.stdout.write( json.dumps({'error': 'Coordinates outside of domain'}) )
    sys.exit()

nc = netCDF4.Dataset(fn, 'r')

c2000 = ts.replace(year=2000)
coffset = iemre.daily_offset(c2000)

cnc = netCDF4.Dataset("/mesonet/data/iemre/mw_dailyc.nc", 'r')

res['data'].append({
    'daily_high_f': "%.1f" % (
       datatypes.temperature(nc.variables['high_tmpk'][offset,j,i], 'K').value('F'),),
    'climate_daily_high_f': "%.1f" % (
       datatypes.temperature(cnc.variables['high_tmpk'][coffset,j,i], 'K').value("F"),),
    'daily_low_f': "%.1f" % (
       datatypes.temperature(nc.variables['low_tmpk'][offset,j,i], 'K').value("F"),),
    'climate_daily_low_f': "%.1f" % (
       datatypes.temperature(cnc.variables['low_tmpk'][coffset,j,i], 'K').value("F"),),
    'daily_precip_in': "%.2f" % (
       nc.variables['p01d'][offset,j,i] / 25.4,),
    'climate_daily_precip_in': "%.2f" % (
       cnc.variables['p01d'][coffset,j,i] / 25.4,),
  })
nc.close()
cnc.close()

sys.stdout.write( json.dumps( res ) )
