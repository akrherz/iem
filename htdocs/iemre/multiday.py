#!/usr/bin/env python

import sys
import cgi
from pyiem import iemre, datatypes
import netCDF4
import datetime
import json
import numpy as np
import warnings
from json import encoder
warnings.simplefilter("ignore", UserWarning)
encoder.FLOAT_REPR = lambda o: format(o, '.2f')


def send_error(msg):
    """ Send an error when something bad happens(tm)"""
    sys.stdout.write('Content-type: application/json\n\n')
    sys.stdout.write(json.dumps({'error': msg}))
    sys.exit()

form = cgi.FormContent()
ts1 = datetime.datetime.strptime(form["date1"][0], "%Y-%m-%d")
ts2 = datetime.datetime.strptime(form["date2"][0], "%Y-%m-%d")
if ts1 >= ts2:
    send_error("date1 larger than date2")
if ts1.year != ts2.year:
    send_error("multi-year query not supported yet...")
# Make sure we aren't in the future
tsend = datetime.date.today()
if ts2.date() >= tsend:
    ts2 = datetime.datetime.now() - datetime.timedelta(days=1)

lat = float(form["lat"][0])
lon = float(form["lon"][0])
if lon < iemre.WEST or lon > iemre.EAST:
    send_error("lon value outside of bounds: %s to %s" % (iemre.WEST,
                                                          iemre.EAST))
if lat < iemre.SOUTH or lat > iemre.NORTH:
    send_error("lat value outside of bounds: %s to %s" % (iemre.SOUTH,
                                                          iemre.NORTH))
fmt = form["format"][0]

i, j = iemre.find_ij(lon, lat)
offset1 = iemre.daily_offset(ts1)
offset2 = iemre.daily_offset(ts2) + 1

# Get our netCDF vars
fp = "/mesonet/data/iemre/%s_mw_daily.nc" % (ts1.year,)
nc = netCDF4.Dataset(fp, 'r')
hightemp = datatypes.temperature(nc.variables['high_tmpk'][offset1:offset2,
                                                           j, i],
                                 'K').value("F")
lowtemp = datatypes.temperature(nc.variables['low_tmpk'][offset1:offset2,
                                                         j, i],
                                'K').value("F")
precip = nc.variables['p01d'][offset1:offset2, j, i] / 25.4
nc.close()

# Get our climatology vars
c2000 = ts1.replace(year=2000)
coffset1 = iemre.daily_offset(c2000)
c2000 = ts2.replace(year=2000)
coffset2 = iemre.daily_offset(c2000) + 1
cnc = netCDF4.Dataset("/mesonet/data/iemre/mw_dailyc.nc", 'r')
chigh = datatypes.temperature(cnc.variables['high_tmpk'][coffset1:coffset2,
                                                         j, i],
                              'K').value("F")
clow = datatypes.temperature(cnc.variables['low_tmpk'][coffset1:coffset2,
                                                       j, i],
                             'K').value("F")
cprecip = cnc.variables['p01d'][coffset1:coffset2, j, i] / 25.4
cnc.close()

if ts1.year > 2010:
    fn = "/mesonet/data/iemre/%s_mw_mrms_daily.nc" % (ts1.year,)
    nc = netCDF4.Dataset(fn, 'r')
    j2 = int((lat - iemre.SOUTH) * 100.0)
    i2 = int((lon - iemre.WEST) * 100.0)
    mrms_precip = nc.variables['p01d'][offset1:offset2, j2, i2] / 25.4
    nc.close()
else:
    mrms_precip = [None]*(offset2-offset1)

res = {'data': [], }


def clean(val):
    if val is None or np.isnan(val) or np.ma.is_masked(val):
        return None
    return float(val)

for i in range(0, offset2 - offset1):
    now = ts1 + datetime.timedelta(days=i)
    res['data'].append({'date': now.strftime("%Y-%m-%d"),
                        'mrms_precip_in': clean(mrms_precip[i]),
                        'daily_high_f': clean(hightemp[i]),
                        'climate_daily_high_f': clean(chigh[i]),
                        'daily_low_f': clean(lowtemp[i]),
                        'climate_daily_low_f': clean(clow[i]),
                        'daily_precip_in': clean(precip[i]),
                        'climate_daily_precip_in': clean(cprecip[i])
                        })


sys.stdout.write('Content-type: application/json\n\n')
sys.stdout.write(json.dumps(res))
