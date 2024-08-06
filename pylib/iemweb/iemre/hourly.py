"""JSON service providing IEMRE data for a given point"""

import datetime
import json
import os
from zoneinfo import ZoneInfo

import numpy as np
from pyiem import iemre
from pyiem.exceptions import BadWebRequest
from pyiem.util import convert_value, ncopen, utc
from pyiem.webutil import iemapp
from pymemcache.client import Client

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
    # This logic does not properly handle spring/fall time changes as it always
    # returns a 24 hour period.
    ts = utc(ts.year, ts.month, ts.day, 12).astimezone(
        ZoneInfo("America/Chicago")
    )
    return ts.replace(hour=0), ts.replace(hour=23)


def workflow(sts, ets, i, j, domain):
    """Return a dict of our data."""
    res = {"data": [], "generated_at": utc().strftime(ISO)}

    # BUG here for Dec 31.
    fn = iemre.get_hourly_ncname(sts.year, domain=domain)

    if not os.path.isfile(fn):
        return res

    if i is None or j is None:
        return {"error": "Coordinates outside of domain"}

    res["grid_i"] = int(i)
    res["grid_j"] = int(j)
    with ncopen(fn) as nc:
        now = sts
        while now <= ets:
            offset = iemre.hourly_offset(now)
            res["data"].append(
                {
                    "valid_utc": now.astimezone(ZoneInfo("UTC")).strftime(ISO),
                    "valid_local": now.strftime(ISO[:-1]),
                    "skyc_%": myrounder(nc.variables["skyc"][offset, j, i], 1),
                    "air_temp_f": myrounder(
                        convert_value(
                            nc.variables["tmpk"][offset, j, i], "degK", "degF"
                        ),
                        1,
                    ),
                    "dew_point_f": myrounder(
                        convert_value(
                            nc.variables["dwpk"][offset, j, i], "degK", "degF"
                        ),
                        1,
                    ),
                    "soil4t_f": myrounder(
                        convert_value(
                            nc.variables["soil4t"][offset, j, i],
                            "degK",
                            "degF",
                        ),
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
    return res


@iemapp()
def application(environ, start_response):
    """Do Something Fun!"""
    try:
        sts, ets = get_timerange(environ)
    except ValueError as exp:
        raise BadWebRequest("Invalid date provided") from exp
    lat = float(environ.get("lat", 41.99))
    lon = float(environ.get("lon", -95.1))
    domain = iemre.get_domain(lon, lat)

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)

    i, j = iemre.find_ij(lon, lat, domain=domain)
    mckey = f"iemre/hourly/{domain}/{sts:%Y%m%d}/{i}/{j}"

    mc = Client("iem-memcached:11211")
    res = mc.get(mckey)
    if res is None:
        res = workflow(sts, ets, i, j, domain)
        res = json.dumps(res).encode("ascii")
        mc.set(mckey, res, 3600)
    mc.close()
    return [res]
