"""Produce geojson of CF6 data"""

import datetime

import simplejson as json
from pyiem.reference import TRACE_VALUE
from pyiem.util import html_escape
from pyiem.webutil import iemapp
from pymemcache.client import Client
from simplejson import encoder

encoder.FLOAT_REPR = lambda o: format(o, ".2f")


def departure(ob, climo):
    """Compute a departure value"""
    if ob is None or climo is None:
        return "M"
    return ob - climo


def int_sanitize(val):
    """convert to Ms"""
    if val is None:
        return "M"
    if val == TRACE_VALUE:
        return "T"
    return int(val)


def f1_sanitize(val):
    """convert to Ms"""
    if val is None:
        return "M"
    if val == TRACE_VALUE:
        return "T"
    return round(val, 1)


def f2_sanitize(val):
    """convert to Ms"""
    if val is None:
        return "M"
    if val == TRACE_VALUE:
        return "T"
    return round(val, 2)


def get_data(cursor, ts, fmt):
    """Get the data for this timestamp"""
    data = {"type": "FeatureCollection", "features": []}
    # Fetch the daily values
    cursor.execute(
        """
    select station, name, product, state, wfo, valid,
    round(st_x(geom)::numeric, 4)::float as st_x,
    round(st_y(geom)::numeric, 4)::float as st_y,
    high, low, avg_temp, dep_temp, hdd, cdd, precip, snow, snowd_12z,
    avg_smph, max_smph, avg_drct, minutes_sunshine, possible_sunshine,
    cloud_ss, wxcodes, gust_smph, gust_drct
    from cf6_data c JOIN stations s on (c.station = s.id)
    WHERE s.network = 'NWSCLI' and c.valid = %s
    """,
        (ts.date(),),
    )
    for i, row in enumerate(cursor):
        data["features"].append(
            {
                "type": "Feature",
                "id": i,
                "properties": {
                    "station": row["station"],
                    "state": row["state"],
                    "valid": row["valid"].strftime("%Y-%m-%d"),
                    "wfo": row["wfo"],
                    "link": f"/api/1/nwstext/{row['product']}",
                    "product": row["product"],
                    "name": row["name"],
                    "high": int_sanitize(row["high"]),
                    "low": int_sanitize(row["low"]),
                    "avg_temp": f1_sanitize(row["avg_temp"]),
                    "dep_temp": f1_sanitize(row["dep_temp"]),
                    "hdd": int_sanitize(row["hdd"]),
                    "cdd": int_sanitize(row["cdd"]),
                    "precip": f2_sanitize(row["precip"]),
                    "snow": f1_sanitize(row["snow"]),
                    "snowd_12z": f1_sanitize(row["snowd_12z"]),
                    "avg_smph": f1_sanitize(row["avg_smph"]),
                    "max_smph": f1_sanitize(row["max_smph"]),
                    "avg_drct": int_sanitize(row["avg_drct"]),
                    "minutes_sunshine": int_sanitize(row["minutes_sunshine"]),
                    "possible_sunshine": int_sanitize(
                        row["possible_sunshine"]
                    ),
                    "cloud_ss": f1_sanitize(row["cloud_ss"]),
                    "wxcodes": row["wxcodes"],
                    "gust_smph": f1_sanitize(row["gust_smph"]),
                    "gust_drct": int_sanitize(row["gust_drct"]),
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [row["st_x"], row["st_y"]],
                },
            }
        )
    if fmt == "geojson":
        return json.dumps(data)
    cols = (
        "station,valid,name,state,wfo,high,low,avg_temp,dep_temp,hdd,cdd,"
        "precip,snow,snowd_12z,avg_smph,max_smph,avg_drct,minutes_sunshine,"
        "possible_sunshine,cloud_ss,wxcodes,gust_smph,gust_drct"
    )
    res = cols + "\n"
    for feat in data["features"]:
        for col in cols.split(","):
            val = feat["properties"][col]
            if isinstance(val, (list, tuple)):
                res += "%s," % (" ".join([str(s) for s in val]),)
            else:
                res += "%s," % (val,)
        res += "\n"
    return res


@iemapp(iemdb="iem", iemdb_cursorname="cursor")
def application(environ, start_response):
    """see how we are called"""
    dt = environ.get("dt", datetime.date.today().strftime("%Y-%m-%d"))
    ts = datetime.datetime.strptime(dt, "%Y-%m-%d")
    cb = environ.get("callback", None)
    fmt = environ.get("fmt", "geojson")

    headers = []
    if fmt == "geojson":
        headers.append(("Content-type", "application/vnd.geo+json"))
    else:
        headers.append(("Content-type", "text/plain"))

    mckey = "/geojson/cf6/%s?callback=%s&fmt=%s" % (
        ts.strftime("%Y%m%d"),
        cb,
        fmt,
    )
    mc = Client("iem-memcached:11211")
    res = mc.get(mckey)
    if not res:
        res = get_data(environ["iemdb.iem.cursor"], ts, fmt)
        mc.set(mckey, res, 300)
    else:
        res = res.decode("utf-8")
    mc.close()
    if cb is not None:
        res = f"{html_escape(cb)}({res})"

    start_response("200 OK", headers)
    return [res.encode("ascii")]
