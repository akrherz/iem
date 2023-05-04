"""Climodat degree days service."""
import datetime
import json

import numpy as np
from metpy.units import units
from paste.request import parse_formvars
from pyiem.iemre import find_ij
from pyiem.meteorology import gdd as calc_gdd
from pyiem.util import c2f, get_dbconn, ncopen
from pymemcache.client import Client


def compute_taxis(ncvar):
    """Figure out our dates."""
    res = []
    basets = datetime.datetime.strptime(
        ncvar.units[:21], "Days since %Y-%m-%d"
    ).date()
    for val in ncvar[:]:
        res.append(basets + datetime.timedelta(days=val))
    return res


def compute(taxis, highs, lows, gddbase, gddceil):
    """Sensibly compute gdds."""
    res = []
    total = 0
    vals = calc_gdd(
        units("degF") * highs, units("degF") * lows, gddbase, gddceil
    )
    for dt, val, high, low in zip(taxis, vals, highs, lows):
        if np.ma.is_masked(val):
            continue
        total += val
        res.append(
            {"date": f"{dt:%Y-%m-%d}", "gdd": val, "high": high, "low": low}
        )
    return res, total


def run(station, sdate, edate, gddbase, gddceil):
    """Do something"""
    with get_dbconn("coop") as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            WITH obs as (
                select sum(gddxx(%s, %s, high, low)) from alldata
                where station = %s and day >= %s and day <= %s)
            select o.sum, st_x(t.geom) as lon, st_y(t.geom) as lat
            from obs o, stations t WHERE t.id = %s
            """,
            (gddbase, gddceil, station, sdate, edate, station),
        )
        accum, lon, lat = [float(x) for x in cursor.fetchone()]
    res = {
        "station": station,
        "sdate": f"{sdate:%Y-%m-%d}",
        "edate": f"{edate:%Y-%m-%d}",
        "gddbase": gddbase,
        "gddceil": gddceil,
        "accum": accum,
    }
    idx, jdx = find_ij(lon, lat)
    for model in ["gfs", "ndfd"]:
        with ncopen(f"/mesonet/data/iemre/{model}_current.nc") as nc:
            highs = c2f(nc.variables["high_tmpk"][:, jdx, idx] - 273.15)
            lows = c2f(nc.variables["low_tmpk"][:, jdx, idx] - 273.15)
            taxis = compute_taxis(nc.variables["time"])
            gdds, total = compute(taxis, highs, lows, gddbase, gddceil)
            res[model] = gdds
            res[f"{model}_accum"] = total
            res[f"{model}_sdate"] = f"{gdds[0]['date']}"
            res[f"{model}_edate"] = f"{gdds[-1]['date']}"

    return json.dumps(res)


def application(environ, start_response):
    """Answer request."""
    fields = parse_formvars(environ)
    station = fields.get("station", "IATAME")[:6].upper()
    today = datetime.date.today() - datetime.timedelta(days=1)
    sdate = datetime.datetime.strptime(
        fields.get("sdate", f"{today.year}-01-01"), "%Y-%m-%d"
    ).date()
    edate = datetime.datetime.strptime(
        fields.get("edate", f"{today:%Y-%m-%d}"), "%Y-%m-%d"
    ).date()
    if edate < sdate:
        sdate, edate = edate, sdate
    gddbase = int(fields.get("gddbase", 50))
    gddceil = int(fields.get("gddceil", 86))

    mckey = f"/json/climodat_dd/{station}/{sdate}/{edate}/{gddbase}/{gddceil}"
    mc = Client("iem-memcached:11211")
    res = mc.get(mckey)
    if res is None:
        res = run(station, sdate, edate, gddbase, gddceil)
        mc.set(mckey, res, 86400)
    else:
        res = res.decode("utf-8")
    mc.close()

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [res.encode("ascii")]
