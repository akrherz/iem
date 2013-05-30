#!/usr/bin/env python

import sys
import cgi
from pyiem import iemre, datatypes
import netCDF4
import datetime
import json

form = cgi.FormContent()
ts1 = datetime.datetime.strptime( form["date1"][0], "%Y-%m-%d")
ts2 = datetime.datetime.strptime( form["date2"][0], "%Y-%m-%d")
if ts1 >= ts2:
    sys.stdout.write('Content-type: application/json\n\n')
    sys.stdout.write( json.dumps( {'error': 'Date1 Larger than Date2', } ) )
    sys.exit()
if ts1.year != ts2.year:
    sys.stdout.write('Content-type: application/json\n\n')
    sys.stdout.write( json.dumps( {'error': 'Multi-year query not supported yet...', } ) )
    sys.exit()
# Make sure we aren't in the future
tsend = datetime.date.today()
if ts2.date() >= tsend:
    ts2 = tsend - datetime.timedelta(days=1)

lat = float( form["lat"][0] )
lon = float( form["lon"][0] )
fmt = form["format"][0]

i,j = iemre.find_ij(lon, lat)
offset1 = iemre.daily_offset(ts1)
offset2 = iemre.daily_offset(ts2) +1

# Get our netCDF vars
fp = "/mesonet/data/iemre/%s_mw_daily.nc" % (ts1.year,)
nc = netCDF4.Dataset(fp, 'r')
hightemp = datatypes.temperature(nc.variables['high_tmpk'][offset1:offset2,j,i], 'K').value("F")
lowtemp = datatypes.temperature(nc.variables['low_tmpk'][offset1:offset2,j,i], 'K').value("F")
precip = nc.variables['p01d'][offset1:offset2,j,i] / 25.4
nc.close()

# Get our climatology vars
c2000 = ts1.replace(year=2000)
coffset1 = iemre.daily_offset(c2000)
c2000 = ts2.replace(year=2000)
coffset2 = iemre.daily_offset(c2000) +1
cnc = netCDF4.Dataset("/mesonet/data/iemre/mw_dailyc.nc", 'r')
chigh = datatypes.temperature(cnc.variables['high_tmpk'][coffset1:coffset2,j,i], 'K').value("F")
clow = datatypes.temperature(cnc.variables['low_tmpk'][coffset1:coffset2,j,i], 'K').value("F")
cprecip = cnc.variables['p01d'][coffset1:coffset2,j,i] / 25.4
cnc.close()

res = {'data': [], }

for i in range(0, offset2 - offset1):
    now = ts1 + datetime.timedelta(days=i)
    res['data'].append({
                'date': now.strftime("%Y-%m-%d"),
    'daily_high_f': "%.1f" % (hightemp[i],),
    'climate_daily_high_f': "%.1f" % (chigh[i],),
    'daily_low_f': "%.1f" % (lowtemp[i],),
    'climate_daily_low_f': "%.1f" % (clow[i],),
    'daily_precip_in': "%.2f" % (precip[i],),
    'climate_daily_precip_in': "%.2f" % (cprecip[i],),
       })


sys.stdout.write('Content-type: application/json\n\n')
sys.stdout.write( json.dumps( res ) )
