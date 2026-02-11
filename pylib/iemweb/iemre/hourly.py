""".. title:: IEMRE Hourly Data Service

This service emits point values from the IEMRE analysis grid.  You can only
request 24 hours of data at a time.

Changelog
---------

- 2026-02-11: Added `tz` parameter to control the timezone used for the
  data response.
- 2026-02-11: The ``generated_at`` metadata was updated to be ISO8601.
- 2025-01-03: Initial implementation with pydantic validation.

"""

import json
import os
from datetime import date as datetype
from datetime import datetime, timedelta, timezone
from typing import Annotated
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import numpy as np
from pydantic import Field, PrivateAttr, field_validator, model_validator
from pyiem.exceptions import IncompleteWebRequest
from pyiem.grid.nav import get_nav
from pyiem.iemre import get_domain, get_hourly_ncname, hourly_offset
from pyiem.reference import ISO8601
from pyiem.util import convert_value, ncopen, utc
from pyiem.webutil import CGIModel, iemapp

ISO = "%Y-%m-%dT%H:%MZ"


class Schema(CGIModel):
    """See how we are called."""

    _domain: Annotated[str, PrivateAttr(None)]
    _i: Annotated[int, PrivateAttr(None)]
    _j: Annotated[int, PrivateAttr(None)]

    date: Annotated[
        datetype, Field(description="Date (for provided tz) to query data for")
    ]
    lat: Annotated[
        float,
        Field(
            le=90,
            ge=-90,
            description="Latitude (degrees Norht) of point to query",
        ),
    ]
    lon: Annotated[
        float,
        Field(
            le=180,
            ge=-180,
            description="Longitude (degrees East) of point to query",
        ),
    ]
    tz: Annotated[
        str,
        Field(
            description=(
                "Timezone of the point to query, for example 'America/Chicago'"
            ),
        ),
    ] = "America/Chicago"

    @field_validator("tz", mode="before")
    @classmethod
    def validate_tz(cls, value):
        """Ensure the timezone is valid."""
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as exp:
            raise ValueError(f"Unknown timezone {value}") from exp
        return value

    @model_validator(mode="after")
    def ensure_domain(self):
        """Ensure the point is within a domain."""
        domain = get_domain(self.lon, self.lat)
        if domain is None:
            raise ValueError("Point is outside all IEMRE domains")
        self._domain = domain  # skipcq
        self._i, self._j = get_nav("iemre", domain).find_ij(
            self.lon, self.lat
        )  # skipcq
        return self


def myrounder(val, precision):
    """round a float or give back None"""
    if val is None or np.isnan(val) or np.ma.is_masked(val):
        return None
    return round(float(val), precision)


def get_timerange(environ: dict) -> tuple[datetime, datetime]:
    """Figure out what period to get data for."""
    tzname = environ["tz"]
    dt = environ["date"]
    # Construct a local midnight to 11 PM period
    ts = datetime(dt.year, dt.month, dt.day, 0, tzinfo=ZoneInfo(tzname))
    return ts, ts.replace(hour=23)


def workflow(
    sts: datetime, ets: datetime, i: int, j: int, domain: str
) -> dict:
    """Return a dict of our data."""
    res = {
        "data": [],
        "grid_i": i,
        "grid_j": j,
        "generated_at": utc().strftime(ISO8601),
    }

    tidx0 = hourly_offset(sts)
    tidx1 = hourly_offset(ets)
    fns = [get_hourly_ncname(sts.astimezone(timezone.utc).year, domain)]
    tslices = [slice(tidx0, tidx1 + 1)]
    if tidx1 < tidx0:
        # We are spanning years
        fns.append(
            get_hourly_ncname(ets.astimezone(timezone.utc).year, domain)
        )
        tslices.append(slice(0, tidx1 + 1))
        tslices[0] = slice(tidx0, None)

    now = sts
    for fn, tslice in zip(fns, tslices, strict=False):
        if not os.path.isfile(fn):
            raise IncompleteWebRequest(
                f"File {fn} does not exist, please try again later"
            )
        with ncopen(fn) as nc:
            skyc = nc.variables["skyc"][tslice, j, i]
            dwpf = convert_value(
                nc.variables["dwpk"][tslice, j, i], "degK", "degF"
            )
            tmpf = convert_value(
                nc.variables["tmpk"][tslice, j, i], "degK", "degF"
            )
            soil4t = convert_value(
                nc.variables["soil4t"][tslice, j, i], "degK", "degF"
            )
            uwnd = nc.variables["uwnd"][tslice, j, i]
            vwnd = nc.variables["vwnd"][tslice, j, i]
            precip = nc.variables["p01m"][tslice, j, i] / 25.4
            for idx, _skyc in enumerate(skyc):
                utcnow = now.astimezone(timezone.utc)
                res["data"].append(
                    {
                        "valid_utc": utcnow.strftime(ISO),
                        "valid_local": now.strftime(ISO[:-1]),
                        "skyc_%": myrounder(_skyc, 1),
                        "air_temp_f": myrounder(tmpf[idx], 1),
                        "dew_point_f": myrounder(dwpf[idx], 1),
                        "soil4t_f": myrounder(soil4t[idx], 1),
                        "uwnd_mps": myrounder(uwnd[idx], 2),
                        "vwnd_mps": myrounder(vwnd[idx], 2),
                        "hourly_precip_in": myrounder(precip[idx], 2),
                    }
                )
                now += timedelta(hours=1)
    return res


def get_mckey(environ: dict):
    """Figure out the memcache key."""
    model: Schema = environ["_cgimodel_schema"]
    return (
        f"iemre/hourly/{model._domain}/{environ['date']:%Y%m%d}"  # skipcq
        f"/{model._i}/{model._j}/{environ['tz']}"  # skipcq
    )


@iemapp(
    help=__doc__, schema=Schema, memcachekey=get_mckey, memcacheexpire=3600
)
def application(environ, start_response):
    """Do Something Fun!"""
    model: Schema = environ["_cgimodel_schema"]
    sts, ets = get_timerange(environ)

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    res = workflow(sts, ets, model._i, model._j, model._domain)  # skipcq
    return json.dumps(res)
