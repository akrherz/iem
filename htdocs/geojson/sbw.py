#!/usr/bin/env python
""" Generate a GeoJSON of current storm based warnings """
import cgi
import datetime
import json

import memcache
import psycopg2.extras
import pytz
from pyiem.util import get_dbconn, ssw, html_escape


def run(ts):
    """ Actually do the hard work of getting the current SBW in geojson """
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if ts == "":
        utcnow = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        t0 = utcnow + datetime.timedelta(days=7)
    else:
        utcnow = datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=pytz.utc
        )
        t0 = utcnow
    sbwtable = "sbw_%s" % (utcnow.year,)

    # Look for polygons into the future as well as we now have Flood products
    # with a start time in the future
    cursor.execute(
        """
        SELECT ST_asGeoJson(geom) as geojson, phenomena, eventid, wfo,
        significance, polygon_end at time zone 'UTC' as utc_polygon_end,
        polygon_begin at time zone 'UTC' as utc_polygon_begin, status
        from """
        + sbwtable
        + """ WHERE
        polygon_begin <= %s and
        polygon_end > %s
    """,
        (t0, utcnow),
    )

    res = {
        "type": "FeatureCollection",
        "features": [],
        "generation_time": utcnow.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": cursor.rowcount,
    }
    for row in cursor:
        sid = "%(wfo)s.%(phenomena)s.%(significance)s.%(eventid)04i" % row
        ets = row["utc_polygon_end"].strftime("%Y-%m-%dT%H:%M:%SZ")
        sts = row["utc_polygon_begin"].strftime("%Y-%m-%dT%H:%M:%SZ")
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
                ),
                geometry=json.loads(row["geojson"]),
            )
        )

    return json.dumps(res)


def main():
    """Main Workflow"""
    ssw("Content-type: application/vnd.geo+json\n\n")

    form = cgi.FieldStorage()
    cb = form.getfirst("callback", None)
    ts = form.getfirst("ts", "")

    mckey = "/geojson/sbw.geojson|%s" % (ts,)
    mc = memcache.Client(["iem-memcached:11211"], debug=0)
    res = mc.get(mckey)
    if not res:
        res = run(ts)
        mc.set(mckey, res, 15 if ts == "" else 3600)

    if cb is None:
        ssw(res)
    else:
        ssw("%s(%s)" % (html_escape(cb), res))


if __name__ == "__main__":
    # Go Main Go
    main()
