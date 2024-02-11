""" JSON service providing hourly Stage IV data for a given point """

import datetime
import json
import os

import numpy as np
from pyiem import iemre
from pyiem.exceptions import IncompleteWebRequest
from pyiem.util import html_escape, mm2inch, ncopen, utc
from pyiem.webutil import iemapp
from pymemcache.client import Client


def myrounder(val, precision):
    """round a float or give back None"""
    if val is None or np.isnan(val) or np.ma.is_masked(val):
        return None
    return round(val, precision)


def dowork(environ):
    """Do work!"""
    date = datetime.datetime.strptime(environ.get("valid"), "%Y-%m-%d")
    lat = float(environ.get("lat"))
    lon = float(environ.get("lon"))

    # We want data for the UTC date and timestamps are in the rears, so from
    # 1z through 1z
    sts = utc(date.year, date.month, date.day, 1)
    ets = sts + datetime.timedelta(hours=24)
    sidx = iemre.hourly_offset(sts)
    eidx = iemre.hourly_offset(ets)

    ncfn = f"/mesonet/data/stage4/{date.year}_stage4_hourly.nc"
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
                "precip_in": myrounder(mm2inch(pt), 2),
            }
        )

    return json.dumps(res)


@iemapp()
def application(environ, start_response):
    """Answer request."""
    if "lat" not in environ:
        raise IncompleteWebRequest("GET parameter lat= missing")
    lat = float(environ.get("lat"))
    lon = float(environ.get("lon"))
    valid = environ.get("valid")
    cb = environ.get("callback", None)

    mckey = f"/json/stage4/{lon:.2f}/{lat:.2f}/{valid}?callback={cb}"
    mc = Client("iem-memcached:11211")
    res = mc.get(mckey)
    if not res:
        res = dowork(environ)
        mc.set(mckey, res, 3600 * 12)
    else:
        res = res.decode("utf-8")
    mc.close()

    if cb is not None:
        res = f"{html_escape(cb)}({res})"

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [res.encode("ascii")]
