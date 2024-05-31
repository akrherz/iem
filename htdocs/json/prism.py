"""JSON service providing PRISM data for a given point"""

import datetime
import json
import os

import numpy as np
from pydantic import Field
from pyiem import prism
from pyiem.exceptions import NoDataFound
from pyiem.util import c2f, mm2inch, ncopen
from pyiem.webutil import CGIModel, iemapp


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function")
    lat: float = Field(41.9, description="Latitude of point")
    lon: float = Field(-92.0, description="Longitude of point")
    valid: str = Field("20191028", description="Valid date to query")


def myrounder(val, precision):
    """round a float or give back None"""
    if val is None or np.isnan(val) or np.ma.is_masked(val):
        return None
    return round(val, precision)


def compute_dates(dstring):
    """Convert the date string into useful things"""
    if len(dstring) == 8:
        return [
            [
                datetime.date(
                    int(dstring[:4]), int(dstring[4:6]), int(dstring[6:8])
                )
            ]
        ]
    if len(dstring) == 17:
        ts1 = datetime.date(
            int(dstring[:4]), int(dstring[4:6]), int(dstring[6:8])
        )
        ts2 = datetime.date(
            int(dstring[9:13]), int(dstring[13:15]), int(dstring[15:17])
        )
        interval = datetime.timedelta(days=1)
        res = [[ts1]]
        now = ts1
        while now <= ts2:
            if now.year != res[-1][0].year:
                res[-1].append(now - datetime.timedelta(days=1))
                res.append([now])
            now += interval
        res[-1].append(now - datetime.timedelta(days=1))
        return res

    return None


def dowork(valid, lon, lat):
    """Do work!"""
    dates = compute_dates(valid)

    i, j = prism.find_ij(lon, lat)
    if i is None or j is None:
        raise NoDataFound("Coordinates outside of domain")

    res = {
        "gridi": int(i),
        "gridj": int(j),
        "data": [],
        "disclaimer": (
            "PRISM Climate Group, Oregon State University, "
            "http://prism.oregonstate.edu, created 4 Feb 2004."
        ),
    }

    if i is None or j is None:
        return "Coordinates outside of domain"

    for dpair in dates:
        sts = dpair[0]
        ets = dpair[-1]
        sidx = prism.daily_offset(sts)
        eidx = prism.daily_offset(ets) + 1

        ncfn = "/mesonet/data/prism/%s_daily.nc" % (sts.year,)
        if not os.path.isfile(ncfn):
            continue
        with ncopen(ncfn) as nc:
            tmax = nc.variables["tmax"][sidx:eidx, j, i]
            tmin = nc.variables["tmin"][sidx:eidx, j, i]
            ppt = nc.variables["ppt"][sidx:eidx, j, i]

        for tx, (mt, nt, pt) in enumerate(zip(tmax, tmin, ppt)):
            valid = sts + datetime.timedelta(days=tx)
            res["data"].append(
                {
                    "valid": valid.strftime("%Y-%m-%dT12:00:00Z"),
                    "high_f": myrounder(c2f(mt), 1),
                    "low_f": myrounder(c2f(nt), 1),
                    "precip_in": myrounder(mm2inch(pt), 2),
                }
            )

    return json.dumps(res)


def get_mckey(environ):
    """get key."""
    return (
        f"/json/prism/{environ['lon']:.2f}/"
        f"{environ['lat']:.2f}/{environ['valid']}"
    )


@iemapp(
    help=__doc__,
    schema=Schema,
    memcachekey=get_mckey,
)
def application(environ, start_response):
    """Answer request."""
    lat = environ["lat"]
    lon = environ["lon"]
    valid = environ["valid"]

    res = dowork(valid, lon, lat)
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return res
