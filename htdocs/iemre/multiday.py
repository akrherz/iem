"""Provide multiday values for IEMRE and friends"""

import datetime
import json
import warnings

import numpy as np
import pyiem.prism as prismutil
from pyiem import iemre
from pyiem.exceptions import IncompleteWebRequest
from pyiem.util import convert_value, ncopen
from pyiem.webutil import iemapp

warnings.simplefilter("ignore", UserWarning)
json.encoder.FLOAT_REPR = lambda o: format(o, ".2f")
json.encoder.c_make_encoder = None


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


@iemapp()
def application(environ, start_response):
    """Go Main Go"""
    if "date1" not in environ:
        raise IncompleteWebRequest("GET date1= parameter missing")
    try:
        ts1 = datetime.datetime.strptime(environ.get("date1"), "%Y-%m-%d")
        ts2 = datetime.datetime.strptime(environ.get("date2"), "%Y-%m-%d")
    except ValueError as exp:
        raise IncompleteWebRequest("Invalid date(s) provided") from exp
    if ts1 > ts2:
        (ts1, ts2) = (ts2, ts1)
    if ts1.year != ts2.year:
        return [
            send_error(start_response, "multi-year query not supported yet...")
        ]
    # Make sure we aren't in the future
    tsend = datetime.date.today()
    if ts2.date() > tsend:
        ts2 = datetime.datetime.now() - datetime.timedelta(days=1)

    lat = float(environ.get("lat"))
    lon = float(environ.get("lon"))
    if lon < iemre.WEST or lon > iemre.EAST:
        return [
            send_error(
                start_response,
                f"lon value outside of bounds: {iemre.WEST} to {iemre.EAST}",
            )
        ]
    if lat < iemre.SOUTH or lat > iemre.NORTH:
        return [
            send_error(
                start_response,
                f"lat value outside of bounds: {iemre.SOUTH} to {iemre.NORTH}",
            )
        ]

    i, j = iemre.find_ij(lon, lat)
    offset1 = iemre.daily_offset(ts1)
    offset2 = iemre.daily_offset(ts2) + 1
    tslice = slice(offset1, offset2)

    # Get our netCDF vars
    with ncopen(iemre.get_daily_ncname(ts1.year)) as nc:
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
    with ncopen(iemre.get_dailyc_ncname()) as cnc:
        chigh = convert_value(
            cnc.variables["high_tmpk"][coffset1:coffset2, j, i], "degK", "degF"
        )
        clow = convert_value(
            cnc.variables["low_tmpk"][coffset1:coffset2, j, i], "degK", "degF"
        )
        cprecip = cnc.variables["p01d"][coffset1:coffset2, j, i] / 25.4

    if ts1.year > 1980:
        i2, j2 = prismutil.find_ij(lon, lat)
        with ncopen(f"/mesonet/data/prism/{ts1.year}_daily.nc") as nc:
            prism_precip = nc.variables["ppt"][tslice, j2, i2] / 25.4
    else:
        prism_precip = [None] * (offset2 - offset1)

    if ts1.year > 2000:
        j2 = int((lat - iemre.SOUTH) * 100.0)
        i2 = int((lon - iemre.WEST) * 100.0)
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
