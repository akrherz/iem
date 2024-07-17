"""JSON service providing hourly Stage IV data for a given point"""

import datetime
import json
import os

import numpy as np
from pydantic import Field
from pyiem import iemre
from pyiem.reference import ISO8601
from pyiem.util import mm2inch, ncopen, utc
from pyiem.webutil import CGIModel, iemapp


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function name")
    lat: float = Field(..., description="Latitude of point")
    lon: float = Field(..., description="Longitude of point")
    valid: datetime.date = Field(..., description="Valid date of data")


def myrounder(val, precision):
    """round a float or give back None"""
    if val is None or np.isnan(val) or np.ma.is_masked(val):
        return None
    return round(val, precision)


def dowork(environ):
    """Do work!"""
    valid = environ["valid"]
    # We want data for the UTC date and timestamps are in the rears, so from
    # 1z through 1z
    sts = utc(valid.year, valid.month, valid.day, 1)
    ets = sts + datetime.timedelta(hours=24)
    sidx = iemre.hourly_offset(sts)
    eidx = iemre.hourly_offset(ets)

    ncfn = f"/mesonet/data/stage4/{valid:%Y}_stage4_hourly.nc"
    res = {
        "generated_at": utc().strftime(ISO8601),
        "gridi": -1,
        "gridj": -1,
        "data": [],
    }
    if not os.path.isfile(ncfn):
        return json.dumps(res)
    with ncopen(ncfn) as nc:
        dist = (
            (nc.variables["lon"][:] - environ["lon"]) ** 2
            + (nc.variables["lat"][:] - environ["lat"]) ** 2
        ) ** 0.5
        (j, i) = np.unravel_index(dist.argmin(), dist.shape)  # noqa
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


def get_mckey(environ):
    """Get the memcachekey."""
    return (
        f"/json/stage4/{environ['lon']:.2f}/{environ['lat']:.2f}/"
        f"{environ['valid']}"
    )


@iemapp(
    help=__doc__, schema=Schema, memcachekey=get_mckey, memcacheexpire=30000
)
def application(environ, start_response):
    """Answer request."""
    res = dowork(environ)
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return res
