#!/usr/bin/env python
""" JSON service providing hourly Stage IV data for a given point """

import datetime
import json
import sys
import cgi

import pytz
from pyiem import iemre, datatypes
import netCDF4
import numpy as np
import memcache


def myrounder(val, precision):
    """round a float or give back None"""
    if val is None or np.isnan(val) or np.ma.is_masked(val):
        return None
    return round(val, precision)


def dowork(form):
    """Do work!"""
    date = datetime.datetime.strptime(form.getfirst('valid'), '%Y-%m-%d')
    lat = float(form.getfirst("lat"))
    lon = float(form.getfirst("lon"))

    # We want data for the UTC date and timestamps are in the rears, so from
    # 1z through 1z
    sts = datetime.datetime(date.year, date.month, date.day, 1)
    sts = sts.replace(tzinfo=pytz.utc)
    ets = sts + datetime.timedelta(hours=24)
    sidx = iemre.hourly_offset(sts)
    eidx = iemre.hourly_offset(ets)

    ncfn = "/mesonet/data/stage4/%s_stage4_hourly.nc" % (date.year, )
    nc = netCDF4.Dataset(ncfn, 'r')

    dist = ((nc.variables['lon'][:] - lon)**2 +
            (nc.variables['lat'][:] - lat)**2)**0.5
    (j, i) = np.unravel_index(dist.argmin(), dist.shape)
    res = {'gridi': i, 'gridj': j, 'data': []}

    ppt = nc.variables['p01m'][sidx:eidx, j, i]
    nc.close()

    for tx, pt in enumerate(ppt):
        valid = sts + datetime.timedelta(hours=tx)
        res['data'].append({
            'end_valid': valid.strftime("%Y-%m-%dT%H:00:00Z"),
            'precip_in': myrounder(
                        datatypes.distance(pt, 'MM').value('IN'), 2)
            })

    return json.dumps(res)


def main():
    """Do Something Fun!"""
    sys.stdout.write("Content-type: application/json\n\n")

    form = cgi.FieldStorage()
    lat = float(form.getfirst('lat'))
    lon = float(form.getfirst('lon'))
    valid = form.getfirst('valid')
    cb = form.getfirst('callback', None)

    mckey = "/json/stage4/%.2f/%.2f/%s?callback=%s" % (lon, lat, valid, cb)
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    if not res:
        res = dowork(form)
        mc.set(mckey, res, 3600*12)

    if cb is None:
        sys.stdout.write(res)
    else:
        sys.stdout.write("%s(%s)" % (cb, res))


if __name__ == '__main__':
    main()
