""".. title:: IEM Reanalysis Daily Data

Return to `API Services </api/#cgi>`_

This service provides access to the IEM Reanalysis daily data product. Some
additional information comes along for the ride.

Changelog
---------

- 2024-09-11: Initial documentation update

Example Requests
----------------

Provide the daily data for a location in Iowa on 1 Jan 2024

https://mesonet.agron.iastate.edu/iemre/daily.py\
?date=2024-01-01&lat=41.99&lon=-95.1

"""

import datetime
import json
import os

import numpy as np
import pyiem.prism as prismutil
from pyiem import iemre
from pyiem.util import convert_value, ncopen
from pyiem.webutil import iemapp


def myrounder(val, precision):
    """round a float or give back None"""
    if val is None or np.isnan(val) or np.ma.is_masked(val):
        return None
    return round(val, precision)


@iemapp(help=__doc__)
def application(environ, start_response):
    """Do Something Fun!"""
    ts = datetime.datetime.strptime(
        environ.get("date", "2019-03-01"), "%Y-%m-%d"
    )
    lat = float(environ.get("lat", 41.99))
    lon = float(environ.get("lon", -95.1))
    fmt = environ.get("format", "json")
    if fmt != "json":
        headers = [("Content-type", "text/plain")]
        start_response("200 OK", headers)
        return [b"ERROR: Service only emits json at this time"]

    i, j = iemre.find_ij(lon, lat)
    offset = iemre.daily_offset(ts)

    res = {"data": []}

    fn = iemre.get_daily_ncname(ts.year)

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)

    if not os.path.isfile(fn):
        return [json.dumps(res).encode("ascii")]

    if i is None or j is None:
        data = {"error": "Coordinates outside of domain"}
        return [json.dumps(data).encode("ascii")]

    if ts.year > 1980:
        ncfn = f"/mesonet/data/prism/{ts.year}_daily.nc"
        if not os.path.isfile(ncfn):
            prism_precip = None
        else:
            i2, j2 = prismutil.find_ij(lon, lat)
            with ncopen(ncfn) as nc:
                prism_precip = nc.variables["ppt"][offset, j2, i2] / 25.4
    else:
        prism_precip = None

    if ts.year > 2000:
        ncfn = iemre.get_daily_mrms_ncname(ts.year)
        if not os.path.isfile(ncfn):
            mrms_precip = None
        else:
            j2 = int((lat - iemre.SOUTH) * 100.0)
            i2 = int((lon - iemre.WEST) * 100.0)
            with ncopen(ncfn) as nc:
                mrms_precip = nc.variables["p01d"][offset, j2, i2] / 25.4
    else:
        mrms_precip = None

    c2000 = ts.replace(year=2000)
    coffset = iemre.daily_offset(c2000)

    with ncopen(fn) as nc, ncopen(iemre.get_dailyc_ncname()) as cnc:
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
