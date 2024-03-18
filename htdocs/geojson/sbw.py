"""Generate a GeoJSON of current storm based warnings"""

import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from pyiem.database import get_sqlalchemy_conn
from pyiem.reference import ISO8601
from pyiem.util import html_escape, utc
from pyiem.webutil import iemapp
from pymemcache.client import Client
from sqlalchemy import text


def run(ts, wfo):
    """Actually do the hard work of getting the current SBW in geojson"""
    if ts == "":
        utcnow = utc()
    else:
        utcnow = datetime.strptime(ts, ISO8601).replace(tzinfo=ZoneInfo("UTC"))
    wfo_limiter = ""
    if wfo is not None:
        wfo_limiter = " and wfo = :wfo "

    res = {
        "type": "FeatureCollection",
        "features": [],
        "generation_time": utc().strftime(ISO8601),
        "valid_at": utcnow.strftime(ISO8601),
    }
    params = {
        "wfo": wfo,
        "utcnow": utcnow,
        "sts": utcnow - timedelta(days=21),
    }

    # NOTE: we dropped checking for products valid in the future (FL.W)
    # NOTE: we have an arb offset check for child table exclusion
    with get_sqlalchemy_conn("postgis") as conn:
        rs = conn.execute(
            text(f"""
            SELECT ST_asGeoJson(geom) as geojson, phenomena, eventid, wfo,
            significance, polygon_end at time zone 'UTC' as utc_polygon_end,
            polygon_begin at time zone 'UTC' as utc_polygon_begin, status,
            hvtec_nwsli, vtec_year, product_id from sbw WHERE
            polygon_begin > :sts and polygon_begin <= :utcnow
            and polygon_end > :utcnow {wfo_limiter}
        """),
            params,
        )
        for _row in rs:
            row = _row._asdict()
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
                        year=row["vtec_year"],
                        product_id=row["product_id"],
                    ),
                    geometry=json.loads(row["geojson"]),
                )
            )
    res["count"] = len(res["features"])
    return json.dumps(res)


def validate_ts(val):
    """see that we have something reasonable."""
    if val == "":
        return val
    year = int(val[:4])
    if year < 1986 or year > (utc().year + 1):
        raise ValueError("year invalid")
    if len(val) == 10:
        val += "T00:00:00Z"
    # YYYY-mm-ddTHH:MI
    if len(val) == 16:
        val += ":00Z"
    return val[:24]


@iemapp()
def application(environ, start_response):
    """Main Workflow"""
    headers = [("Content-type", "application/vnd.geo+json")]

    cb = environ.get("callback", None)
    wfo = environ.get("wfo")
    try:
        ts = validate_ts(environ.get("ts", "").strip())
    except Exception:
        start_response("500 Internal Server Error", headers)
        return ["{'error': 'ts is malformed'}".encode("ascii")]

    mckey = f"/geojson/sbw.geojson|{ts}|{wfo}"
    mc = Client("iem-memcached:11211")
    res = mc.get(mckey)
    if not res:
        res = run(ts, wfo)
        mc.set(mckey, res, 15 if ts == "" else 3600)
    else:
        res = res.decode("utf-8")
    mc.close()
    if cb is not None:
        res = f"{html_escape(cb)}({res})"

    start_response("200 OK", headers)
    return [res.encode("ascii")]
