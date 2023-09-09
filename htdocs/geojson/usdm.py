""" Generate a GeoJSON of US Drought Monitor"""
import datetime
import json

import psycopg2.extras
from paste.request import parse_formvars
from pyiem.util import get_dbconn, html_escape
from pymemcache.client import Client


def rectify_date(tstamp):
    """Convert this tstamp into something we can actually use

    if '', use max valid from database
    if between tuesday and thursday at 8 AM, go back to last week
    back to tuesday
    """
    if tstamp == "":
        pgconn = get_dbconn("postgis")
        cursor = pgconn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # Go get the latest USDM stored in the database!
        cursor.execute("SELECT max(valid) from usdm")
        return cursor.fetchone()["max"]

    ts = datetime.datetime.strptime(tstamp, "%Y-%m-%d").date()
    offset = (ts.weekday() - 1) % 7
    return ts - datetime.timedelta(days=offset)


def run(ts):
    """Actually do the hard work of getting the USDM in geojson"""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Look for polygons into the future as well as we now have Flood products
    # with a start time in the future
    cursor.execute(
        "SELECT ST_asGeoJson(geom) as geojson, dm, valid "
        "from usdm WHERE valid = %s ORDER by dm ASC",
        (ts,),
    )
    if cursor.rowcount == 0:
        # go back one week
        cursor.execute(
            "SELECT ST_asGeoJson(geom) as geojson, dm, valid "
            "from usdm WHERE valid = %s ORDER by dm ASC",
            (ts - datetime.timedelta(days=7),),
        )

    utcnow = datetime.datetime.utcnow()
    res = {
        "type": "FeatureCollection",
        "features": [],
        "generation_time": utcnow.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": cursor.rowcount,
    }
    for row in cursor:
        res["features"].append(
            dict(
                type="Feature",
                id=row["dm"],
                properties=dict(
                    date=row["valid"].strftime("%Y-%m-%d"), dm=row["dm"]
                ),
                geometry=json.loads(row["geojson"]),
            )
        )

    return json.dumps(res)


def application(environ, start_response):
    """Main Workflow"""
    headers = [("Content-type", "application/vnd.geo+json")]

    form = parse_formvars(environ)
    cb = form.get("callback", None)
    tstr = form.get("date", "")
    if tstr == "qqq":  # from pyIEM automation
        headers = [("Content-type", "text/plain")]
        start_response("500 Internal Server Error", headers)
        return [b"Sorry, I don't know how to handle this request"]
    ts = rectify_date(tstr)

    mckey = f"/geojson/usdm.geojson|{ts}"
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
