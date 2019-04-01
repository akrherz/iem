#!/usr/bin/env python
""" JSON service providing PRISM data for a given point """
import os
import datetime
import json
import cgi

import numpy as np
import memcache
from pyiem import prism, datatypes
from pyiem.util import ncopen, ssw


def myrounder(val, precision):
    """round a float or give back None"""
    if val is None or np.isnan(val) or np.ma.is_masked(val):
        return None
    return round(val, precision)


def compute_dates(dstring):
    """Convert the date string into useful things"""
    if len(dstring) == 8:
        return [[datetime.date(int(dstring[:4]), int(dstring[4:6]),
                               int(dstring[6:8])), ], ]
    if len(dstring) == 17:
        ts1 = datetime.date(int(dstring[:4]), int(dstring[4:6]),
                            int(dstring[6:8]))
        ts2 = datetime.date(int(dstring[9:13]), int(dstring[13:15]),
                            int(dstring[15:17]))
        interval = datetime.timedelta(days=1)
        res = [[ts1, ]]
        now = ts1
        while now <= ts2:
            if now.year != res[-1][0].year:
                res[-1].append(now - datetime.timedelta(days=1))
                res.append([now, ])
            now += interval
        res[-1].append(now - datetime.timedelta(days=1))
        return res

    return None


def dowork(form):
    """Do work!"""
    dates = compute_dates(form.getfirst('valid'))
    lat = float(form.getfirst("lat"))
    lon = float(form.getfirst("lon"))

    i, j = prism.find_ij(lon, lat)

    res = {'gridi': int(i), 'gridj': int(j), 'data': [],
           'disclaimer': ("PRISM Climate Group, Oregon State University, "
                          "http://prism.oregonstate.edu, created 4 Feb 2004.")}

    if i is None or j is None:
        ssw(json.dumps({'error': 'Coordinates outside of domain'}))
        return

    for dpair in dates:
        sts = dpair[0]
        ets = dpair[-1]
        sidx = prism.daily_offset(sts)
        eidx = prism.daily_offset(ets) + 1

        ncfn = "/mesonet/data/prism/%s_daily.nc" % (sts.year, )
        if not os.path.isfile(ncfn):
            continue
        nc = ncopen(ncfn)

        tmax = nc.variables['tmax'][sidx:eidx, j, i]
        tmin = nc.variables['tmin'][sidx:eidx, j, i]
        ppt = nc.variables['ppt'][sidx:eidx, j, i]
        nc.close()

        for tx, (mt, nt, pt) in enumerate(zip(tmax, tmin, ppt)):
            valid = sts + datetime.timedelta(days=tx)
            res['data'].append({
                'valid': valid.strftime("%Y-%m-%dT12:00:00Z"),
                'high_f': myrounder(
                            datatypes.temperature(mt, 'C').value('F'), 1),
                'low_f': myrounder(
                            datatypes.temperature(nt, 'C').value('F'), 1),
                'precip_in': myrounder(
                            datatypes.distance(pt, 'MM').value('IN'), 2)
                })

    return json.dumps(res)


def main():
    """Do Something Fun!"""
    ssw("Content-type: application/json\n\n")

    form = cgi.FieldStorage()
    lat = float(form.getfirst('lat'))
    lon = float(form.getfirst('lon'))
    valid = form.getfirst('valid')
    cb = form.getfirst('callback', None)

    mckey = "/json/prism/%.2f/%.2f/%s?callback=%s" % (lon, lat, valid, cb)
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    if not res:
        res = dowork(form)
        mc.set(mckey, res, 3600*12)

    if cb is None:
        ssw(res)
    else:
        ssw("%s(%s)" % (cgi.escape(cb, quote=True), res))


if __name__ == '__main__':
    main()
