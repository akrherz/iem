""".. title:: IEMRE Multi-Day Data

Return to `JSON Services </json/>`_

Documentation for /iemre/multiday.py
------------------------------------

This application provides a JSON service for multi-day data from the IEM
Reanalysis project.

Example Usage
-------------

Get July 2024 data for Ames, IA:

https:://mesonet.agron.iastate.edu/iemre/multiday.py?date1=2024-07-01&\
date2=2024-07-31&lat=42.0308&lon=-93.6319

"""

import datetime
import json
import warnings

import numpy as np
import pyiem.prism as prismutil
from pydantic import Field
from pyiem import iemre
from pyiem.util import convert_value, ncopen
from pyiem.webutil import CGIModel, iemapp

warnings.simplefilter("ignore", UserWarning)
json.encoder.FLOAT_REPR = lambda o: format(o, ".2f")
json.encoder.c_make_encoder = None


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function name")
    date1: datetime.date = Field(
        ..., description="Start date for the data request, YYYY-MM-DD"
    )
    date2: datetime.date = Field(
        ..., description="End date for the data request, YYYY-MM-DD"
    )
    lat: float = Field(
        ...,
        description="Latitude of the point of interest, decimal degrees",
        ge=-90,
        le=90,
    )
    lon: float = Field(
        ...,
        description="Longitude of the point of interest, decimal degrees",
        ge=-180,
        le=180,
    )


def clean(val, precision=2):
    """My filter"""
    if val is None or np.isnan(val) or np.ma.is_masked(val):
        return None
    return round(float(val), precision)


def send_error(start_response, msg):
    """Send an error when something bad happens(tm)"""
    headers = [("Content-type", "application/json")]
    start_response("500 Internal Server Error", headers)
    return json.dumps({"error": msg}).encode("ascii")


@iemapp(help=__doc__, schema=Schema)
def application(environ, start_response):
    """Go Main Go"""
    ts1 = environ["date1"]
    ts2 = environ["date2"]
    if ts1 > ts2:
        (ts1, ts2) = (ts2, ts1)
    if ts1.year != ts2.year:
        return [
            send_error(start_response, "multi-year query not supported yet...")
        ]
    # Make sure we aren't in the future
    tsend = datetime.date.today()
    if ts2 > tsend:
        ts2 = datetime.datetime.now() - datetime.timedelta(days=1)

    lon = environ["lon"]
    lat = environ["lat"]
    domain = iemre.get_domain(lon, lat)
    if domain is None:
        return [
            send_error(
                start_response,
                "Point not within any domain",
            )
        ]
    dom = iemre.DOMAINS[domain]
    i, j = iemre.find_ij(lon, lat, domain=domain)
    offset1 = iemre.daily_offset(ts1)
    offset2 = iemre.daily_offset(ts2) + 1
    tslice = slice(offset1, offset2)

    # Get our netCDF vars
    with ncopen(iemre.get_daily_ncname(ts1.year, domain=domain)) as nc:
        hightemp = convert_value(
            nc.variables["high_tmpk"][tslice, j, i], "degK", "degF"
        )
        high12temp = convert_value(
            nc.variables["high_tmpk_12z"][tslice, j, i],
            "degK",
            "degF",
        )
        lowtemp = convert_value(
            nc.variables["low_tmpk"][tslice, j, i], "degK", "degF"
        )
        avgdwpf = convert_value(
            nc.variables["avg_dwpk"][tslice, j, i], "degK", "degF"
        )
        low12temp = convert_value(
            nc.variables["low_tmpk_12z"][tslice, j, i], "degK", "degF"
        )
        high_soil4t = convert_value(
            nc.variables["high_soil4t"][tslice, j, i], "degK", "degF"
        )
        low_soil4t = convert_value(
            nc.variables["low_soil4t"][tslice, j, i], "degK", "degF"
        )
        precip = nc.variables["p01d"][tslice, j, i] / 25.4
        precip12 = nc.variables["p01d_12z"][tslice, j, i] / 25.4
        # Solar radiation is average W/m2, we want MJ/day
        srad = nc.variables["rsds"][tslice, j, i] / 1e6 * 86400.0

    # Get our climatology vars
    c2000 = ts1.replace(year=2000)
    coffset1 = iemre.daily_offset(c2000)
    c2000 = ts2.replace(year=2000)
    coffset2 = iemre.daily_offset(c2000) + 1
    with ncopen(iemre.get_dailyc_ncname(domain=domain)) as cnc:
        chigh = convert_value(
            cnc.variables["high_tmpk"][coffset1:coffset2, j, i], "degK", "degF"
        )
        clow = convert_value(
            cnc.variables["low_tmpk"][coffset1:coffset2, j, i], "degK", "degF"
        )
        cprecip = cnc.variables["p01d"][coffset1:coffset2, j, i] / 25.4

    if ts1.year > 1980 and domain == "":
        i2, j2 = prismutil.find_ij(lon, lat)
        if i2 is None or j2 is None:
            prism_precip = [None] * (offset2 - offset1)
        else:
            with ncopen(f"/mesonet/data/prism/{ts1.year}_daily.nc") as nc:
                prism_precip = nc.variables["ppt"][tslice, j2, i2] / 25.4
    else:
        prism_precip = [None] * (offset2 - offset1)

    if ts1.year > 2000 and domain == "":
        j2 = int((lat - dom["south"]) * 100.0)
        i2 = int((lon - dom["west"]) * 100.0)
        with ncopen(iemre.get_daily_mrms_ncname(ts1.year)) as nc:
            mrms_precip = nc.variables["p01d"][tslice, j2, i2] / 25.4
    else:
        mrms_precip = [None] * (offset2 - offset1)

    res = {"data": []}

    for i in range(offset2 - offset1):
        now = ts1 + datetime.timedelta(days=i)
        res["data"].append(
            {
                "date": now.strftime("%Y-%m-%d"),
                "mrms_precip_in": clean(mrms_precip[i]),
                "prism_precip_in": clean(prism_precip[i]),
                "daily_high_f": clean(hightemp[i]),
                "12z_high_f": clean(high12temp[i]),
                "climate_daily_high_f": clean(chigh[i]),
                "daily_low_f": clean(lowtemp[i]),
                "12z_low_f": clean(low12temp[i]),
                "avg_dewpoint_f": clean(avgdwpf[i]),
                "soil4t_high_f": clean(high_soil4t[i]),
                "soil4t_low_f": clean(low_soil4t[i]),
                "climate_daily_low_f": clean(clow[i]),
                "daily_precip_in": clean(precip[i]),
                "12z_precip_in": clean(precip12[i]),
                "climate_daily_precip_in": clean(cprecip[i]),
                "solar_mj": clean(srad[i]),
            }
        )

    start_response("200 OK", [("Content-type", "application/json")])
    return [json.dumps(res).encode("ascii")]
