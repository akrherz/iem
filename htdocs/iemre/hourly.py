#!/usr/bin/env python
""" JSON service providing IEMRE data for a given point """
import os
import datetime
import json

import numpy as np
from paste.request import parse_formvars
import pytz
from pyiem import iemre, datatypes
from pyiem.util import ncopen, utc

ISO = "%Y-%m-%dT%H:%MZ"


def myrounder(val, precision):
    """round a float or give back None"""
    if val is None or np.isnan(val) or np.ma.is_masked(val):
        return None
    return round(float(val), precision)


def get_timerange(form):
    """Figure out what period to get data for."""
    ts = datetime.datetime.strptime(form.get("date", "2019-03-01"), "%Y-%m-%d")
    # Construct a CDT/CST Midnight to 11 PM period
    ts = utc(ts.year, ts.month, ts.day, 12).astimezone(
        pytz.timezone("America/Chicago")
    )
    return ts.replace(hour=0), ts.replace(hour=23)


def application(environ, start_response):
    """Do Something Fun!"""
    form = parse_formvars(environ)
    sts, ets = get_timerange(form)
    lat = float(form.get("lat", 41.99))
    lon = float(form.get("lon", -95.1))
    fmt = form.get("format", "json")
    if fmt != "json":
        headers = [("Content-type", "text/plain")]
        start_response("200 OK", headers)
        return [b"ERROR: Service only emits json at this time"]

    i, j = iemre.find_ij(lon, lat)

    res = {"data": []}

    # BUG here for Dec 31.
    fn = iemre.get_hourly_ncname(sts.year)

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)

    if not os.path.isfile(fn):
        return [json.dumps(res).encode("ascii")]

    if i is None or j is None:
        data = {"error": "Coordinates outside of domain"}
        return [json.dumps(data).encode("ascii")]

    with ncopen(fn) as nc:
        now = sts
        while now <= ets:
            offset = iemre.hourly_offset(now)
            res["data"].append(
                {
                    "valid_utc": now.astimezone(pytz.UTC).strftime(ISO),
                    "valid_local": now.strftime(ISO),
                    "skyc_%": myrounder(nc.variables["skyc"][offset, j, i], 1),
                    "air_temp_f": myrounder(
                        datatypes.temperature(
                            nc.variables["tmpk"][offset, j, i], "K"
                        ).value("F"),
                        1,
                    ),
                    "dew_point_f": myrounder(
                        datatypes.temperature(
                            nc.variables["dwpk"][offset, j, i], "K"
                        ).value("F"),
                        1,
                    ),
                    "uwnd_mps": myrounder(
                        nc.variables["uwnd"][offset, j, i], 2
                    ),
                    "vwnd_mps": myrounder(
                        nc.variables["vwnd"][offset, j, i], 2
                    ),
                    "hourly_precip_in": myrounder(
                        nc.variables["p01m"][offset, j, i] / 25.4, 2
                    ),
                }
            )
            now += datetime.timedelta(hours=1)
    return [json.dumps(res).encode("ascii")]
