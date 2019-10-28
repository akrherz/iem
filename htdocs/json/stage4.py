#!/usr/bin/env python
""" JSON service providing hourly Stage IV data for a given point """

import datetime
import json
import os

import numpy as np
import memcache
from paste.request import parse_formvars
from pyiem import iemre, datatypes
from pyiem.util import utc, ncopen, html_escape


def myrounder(val, precision):
    """round a float or give back None"""
    if val is None or np.isnan(val) or np.ma.is_masked(val):
        return None
    return round(val, precision)


def dowork(fields):
    """Do work!"""
    date = datetime.datetime.strptime(fields.get("valid"), "%Y-%m-%d")
    lat = float(fields.get("lat"))
    lon = float(fields.get("lon"))

    # We want data for the UTC date and timestamps are in the rears, so from
    # 1z through 1z
    sts = utc(date.year, date.month, date.day, 1)
    ets = sts + datetime.timedelta(hours=24)
    sidx = iemre.hourly_offset(sts)
    eidx = iemre.hourly_offset(ets)

    ncfn = "/mesonet/data/stage4/%s_stage4_hourly.nc" % (date.year,)
    res = {"gridi": -1, "gridj": -1, "data": []}
    if not os.path.isfile(ncfn):
        return json.dumps(res)
    with ncopen(ncfn) as nc:
        dist = (
            (nc.variables["lon"][:] - lon) ** 2
            + (nc.variables["lat"][:] - lat) ** 2
        ) ** 0.5
        (j, i) = np.unravel_index(dist.argmin(), dist.shape)
        res["gridi"] = int(i)
        res["gridj"] = int(j)

        ppt = nc.variables["p01m"][sidx:eidx, j, i]

    for tx, pt in enumerate(ppt):
        valid = sts + datetime.timedelta(hours=tx)
        res["data"].append(
            {
                "end_valid": valid.strftime("%Y-%m-%dT%H:00:00Z"),
                "precip_in": myrounder(
                    datatypes.distance(pt, "MM").value("IN"), 2
                ),
            }
        )

    return json.dumps(res)


def application(environ, start_response):
    """Answer request."""
    fields = parse_formvars(environ)
    lat = float(fields.get("lat"))
    lon = float(fields.get("lon"))
    valid = fields.get("valid")
    cb = fields.get("callback", None)

    mckey = "/json/stage4/%.2f/%.2f/%s?callback=%s" % (lon, lat, valid, cb)
    mc = memcache.Client(["iem-memcached:11211"], debug=0)
    res = mc.get(mckey)
    if not res:
        res = dowork(fields)
        mc.set(mckey, res, 3600 * 12)

    if cb is None:
        data = res
    else:
        data = "%s(%s)" % (html_escape(cb), res)

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [data.encode("ascii")]
