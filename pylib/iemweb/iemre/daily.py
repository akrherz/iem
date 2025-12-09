""".. title:: IEM Reanalysis Daily Data

Return to `API Services </api/#cgi>`_

This service provides access to the IEM Reanalysis daily data product. Some
additional information comes along for the ride.

Changelog
---------

- 2025-01-01: Implementation updated to use pydantic validation.
- 2024-09-11: Initial documentation update

Example Requests
----------------

Provide the daily data for a location in Iowa on 1 Jan 2024

https://mesonet.agron.iastate.edu/iemre/daily.py\
?date=2024-01-01&lat=41.99&lon=-95.1

"""

import json
import os
from datetime import date as dateobj

import numpy as np
from pydantic import Field
from pyiem.exceptions import NoDataFound
from pyiem.grid.nav import get_nav
from pyiem.iemre import (
    daily_offset,
    get_daily_mrms_ncname,
    get_daily_ncname,
    get_dailyc_ncname,
    get_domain,
)
from pyiem.util import convert_value, ncopen
from pyiem.webutil import CGIModel, iemapp


class Schema(CGIModel):
    """See how we are called."""

    date: dateobj = Field(
        dateobj(2019, 3, 1),
        title="Date",
        description="Date of interest",
    )
    lat: float = Field(
        41.99,
        title="Latitude",
        description="Latitude of interest",
        ge=-90,
        le=90,
    )
    lon: float = Field(
        -95.1,
        title="Longitude",
        description="Longitude of interest",
        ge=-180,
        le=180,
    )
    format: str = Field(
        "json",
        title="Format",
        description="Format of the output",
        pattern="json",
    )


def myrounder(val, precision):
    """round a float or give back None"""
    if val is None or np.isnan(val) or np.ma.is_masked(val):
        return None
    return round(val, precision)


@iemapp(help=__doc__, schema=Schema)
def application(environ, start_response):
    """Do Something Fun!"""
    dt: dateobj = environ["date"]
    lat = environ["lat"]
    lon = environ["lon"]
    domain = get_domain(lon, lat)
    if domain is None:
        raise NoDataFound("Location is outside of IEMRE domains!")
    nav = get_nav("iemre", domain)

    i, j = nav.find_ij(lon, lat)
    offset = daily_offset(dt)

    res = {"data": []}

    fn = get_daily_ncname(dt.year, domain=domain)

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)

    if not os.path.isfile(fn):
        return [json.dumps(res).encode("ascii")]

    if dt.year > 1980 and domain == "conus":
        ncfn = f"/mesonet/data/prism/{dt.year}_daily.nc"
        if not os.path.isfile(ncfn):
            prism_precip = None
        else:
            i2, j2 = get_nav("prism").find_ij(lon, lat)
            with ncopen(ncfn) as nc:
                prism_precip = nc.variables["ppt"][offset, j2, i2] / 25.4
    else:
        prism_precip = None

    if dt.year > 2000 and domain == "conus":
        ncfn = get_daily_mrms_ncname(dt.year)
        if not os.path.isfile(ncfn):
            mrms_precip = None
        else:
            i2, j2 = get_nav("mrms_iemre").find_ij(lon, lat)
            with ncopen(ncfn) as nc:
                mrms_precip = nc.variables["p01d"][offset, j2, i2] / 25.4
    else:
        mrms_precip = None

    c2000 = dt.replace(year=2000)
    coffset = daily_offset(c2000)

    with ncopen(fn) as nc, ncopen(get_dailyc_ncname(domain)) as cnc:
        res["data"].append(
            {
                "prism_precip_in": myrounder(prism_precip, 2),
                "mrms_precip_in": myrounder(mrms_precip, 2),
                "daily_high_f": myrounder(
                    convert_value(
                        nc.variables["high_tmpk"][offset, j, i],
                        "degK",
                        "degF",
                    ),
                    1,
                ),
                "12z_high_f": myrounder(
                    convert_value(
                        nc.variables["high_tmpk_12z"][offset, j, i],
                        "degK",
                        "degF",
                    ),
                    1,
                ),
                "climate_daily_high_f": myrounder(
                    convert_value(
                        cnc.variables["high_tmpk"][coffset, j, i],
                        "degK",
                        "degF",
                    ),
                    1,
                ),
                "daily_low_f": myrounder(
                    convert_value(
                        nc.variables["low_tmpk"][offset, j, i],
                        "degK",
                        "degF",
                    ),
                    1,
                ),
                "12z_low_f": myrounder(
                    convert_value(
                        nc.variables["low_tmpk_12z"][offset, j, i],
                        "degK",
                        "degF",
                    ),
                    1,
                ),
                "soil4t_high_f": myrounder(
                    convert_value(
                        nc.variables["high_soil4t"][offset, j, i],
                        "degK",
                        "degF",
                    ),
                    1,
                ),
                "soil4t_low_f": myrounder(
                    convert_value(
                        nc.variables["low_soil4t"][offset, j, i],
                        "degK",
                        "degF",
                    ),
                    1,
                ),
                "avg_dewpoint_f": myrounder(
                    convert_value(
                        nc.variables["avg_dwpk"][offset, j, i],
                        "degK",
                        "degF",
                    ),
                    1,
                ),
                "climate_daily_low_f": myrounder(
                    convert_value(
                        cnc.variables["low_tmpk"][coffset, j, i],
                        "degK",
                        "degF",
                    ),
                    1,
                ),
                "daily_precip_in": myrounder(
                    nc.variables["p01d"][offset, j, i] / 25.4, 2
                ),
                "12z_precip_in": myrounder(
                    nc.variables["p01d_12z"][offset, j, i] / 25.4, 2
                ),
                "climate_daily_precip_in": myrounder(
                    cnc.variables["p01d"][coffset, j, i] / 25.4, 2
                ),
                "srad_mj": myrounder(
                    nc.variables["rsds"][offset, j, i] * 86400.0 / 1000000.0,
                    2,
                ),
                "avg_windspeed_mps": myrounder(
                    nc.variables["wind_speed"][offset, j, i], 2
                ),
            }
        )
    return [json.dumps(res).encode("ascii")]
