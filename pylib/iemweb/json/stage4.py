""".. title:: JSON Service for Stage IV Precipitation Data

Return to `API Services </api/#json>`_

Documentation for /json/stage4.py
---------------------------------

This emits hourly precipitation data from the Stage IV precipitation dataset
for a given date, which defaults to UTC, but can be specified by the given
`tz` parameter.  Please note that this is not a pure stage IV service, but
includes some bias correcting that the IEM does against PRISM.

Changelog
---------

- 2024-08-19: Added support for tz parameter

Example Usage
-------------

Provide hourly stage IV estimates for 13 August 2024 for 102.3W, 45.1N for
a date in US/Central timezone.

https://mesonet.agron.iastate.edu/json/stage4.py\
?lon=-102.3&lat=45.1&valid=2024-08-13&tz=America/Chicago

"""

import json
import os
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import numpy as np
from pydantic import Field, field_validator
from pyiem import iemre
from pyiem.reference import ISO8601
from pyiem.util import mm2inch, ncopen, utc
from pyiem.webutil import CGIModel, iemapp


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function name")
    lat: float = Field(..., description="Latitude of point")
    lon: float = Field(..., description="Longitude of point")
    valid: date = Field(..., description="Valid date of data")
    tz: str = Field("UTC", description="Timezone of valid date")

    @field_validator("tz")
    @classmethod
    def validate_tz(cls, value):
        """Ensure the timezone is valid."""
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as exp:
            raise ValueError(f"Unknown timezone {value}") from exp
        return value


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
    sts = datetime(
        valid.year, valid.month, valid.day, 1, tzinfo=ZoneInfo(environ["tz"])
    )
    ets = sts + timedelta(hours=24)
    sidx = iemre.hourly_offset(sts)
    eidx = iemre.hourly_offset(ets)

    ncfn = f"/mesonet/data/stage4/{valid:%Y}_stage4_hourly.nc"
    res = {
        "generated_at": utc().strftime(ISO8601),
        "gridi": -1,
        "gridj": -1,
        "for_date_in_timezone": environ["tz"],
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
        valid = sts + timedelta(hours=tx)
        utcnow = valid.astimezone(ZoneInfo("UTC"))
        res["data"].append(
            {
                "end_valid": utcnow.strftime("%Y-%m-%dT%H:00:00Z"),
                "precip_in": myrounder(mm2inch(pt), 2),
            }
        )

    return json.dumps(res)


def get_mckey(environ):
    """Get the memcachekey."""
    return (
        f"/json/stage4/{environ['lon']:.2f}/{environ['lat']:.2f}/"
        f"{environ['valid']}/{environ['tz']}"
    )


@iemapp(
    help=__doc__, schema=Schema, memcachekey=get_mckey, memcacheexpire=3600
)
def application(environ, start_response):
    """Answer request."""
    res = dowork(environ)
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return res
