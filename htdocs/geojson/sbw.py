""" Generate a GeoJSON of current storm based warnings """
import datetime
import json
from zoneinfo import ZoneInfo

from pyiem.reference import ISO8601
from pyiem.util import get_dbconnc, html_escape, utc
from pyiem.webutil import iemapp
from pymemcache.client import Client


def run(ts):
    """Actually do the hard work of getting the current SBW in geojson"""
    pgconn, cursor = get_dbconnc("postgis")

    if ts == "":
        utcnow = utc()
        t0 = utcnow + datetime.timedelta(days=7)
    else:
        utcnow = datetime.datetime.strptime(ts, ISO8601).replace(
            tzinfo=ZoneInfo("UTC")
        )
        t0 = utcnow
    sbwtable = f"sbw_{utcnow.year}"

    # Look for polygons into the future as well as we now have Flood products
    # with a start time in the future
    cursor.execute(
        f"""
        SELECT ST_asGeoJson(geom) as geojson, phenomena, eventid, wfo,
        significance, polygon_end at time zone 'UTC' as utc_polygon_end,
        polygon_begin at time zone 'UTC' as utc_polygon_begin, status,
        hvtec_nwsli
        from {sbwtable} WHERE
        polygon_begin <= %s and
        polygon_end > %s
    """,
        (t0, utcnow),
    )

    res = {
        "type": "FeatureCollection",
        "features": [],
        "generation_time": utcnow.strftime(ISO8601),
        "count": cursor.rowcount,
    }
    for row in cursor:
        sid = (
            f"{row['wfo']}.{row['phenomena']}.{row['significance']}."
            f"{row['eventid']:04.0f}"
        )
        ets = row["utc_polygon_end"].strftime(ISO8601)
        sts = row["utc_polygon_begin"].strftime(ISO8601)
        sid += "." + sts
        res["features"].append(
            dict(
                type="Feature",
                id=sid,
                properties=dict(
                    status=row["status"],
                    phenomena=row["phenomena"],
                    significance=row["significance"],
                    wfo=row["wfo"],
                    eventid=row["eventid"],
                    polygon_begin=sts,
                    expire=ets,
                    hvtec_nwsli=row["hvtec_nwsli"],
                ),
                geometry=json.loads(row["geojson"]),
            )
        )
    pgconn.close()
    return json.dumps(res)


def validate_ts(val):
    """see that we have something reasonable."""
    if val == "":
        return val
    year = int(val[:4])
    if year < 1986 or year > (utc().year + 1):
        raise ValueError("year invalid")
    # YYYY-mm-ddTHH:MI
    if len(val) == 16:
        val += ":00Z"
    return val[:24]


@iemapp()
def application(environ, start_response):
    """Main Workflow"""
    headers = [("Content-type", "application/vnd.geo+json")]

    cb = environ.get("callback", None)
    try:
        ts = validate_ts(environ.get("ts", "").strip())
    except Exception:
        start_response("500 Internal Server Error", headers)
        return ["{'error': 'ts is malformed'}".encode("ascii")]

    mckey = f"/geojson/sbw.geojson|{ts}"
    mc = Client("iem-memcached:11211")
    res = mc.get(mckey)
    if not res:
        res = run(ts)
        mc.set(mckey, res, 15 if ts == "" else 3600)
    else:
        res = res.decode("utf-8")
    mc.close()
    if cb is not None:
        res = f"{html_escape(cb)}({res})"

    start_response("200 OK", headers)
    return [res.encode("ascii")]
