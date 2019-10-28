#!/usr/bin/env python
"""GeoJSON of a given IEM network code"""
import cgi
import json
import datetime

import psycopg2.extras
import memcache
from pyiem.util import get_dbconn, ssw, html_escape


def run(network):
    """Generate a GeoJSON dump of the provided network"""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute(
        """
        SELECT ST_asGeoJson(geom, 4) as geojson, * from stations
        WHERE network = %s ORDER by name ASC
    """,
        (network,),
    )

    res = {
        "type": "FeatureCollection",
        "features": [],
        "generation_time": datetime.datetime.utcnow().strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "count": cursor.rowcount,
    }
    for row in cursor:
        res["features"].append(
            dict(
                type="Feature",
                id=row["id"],
                properties=dict(
                    elevation=row["elevation"],
                    sname=row["name"],
                    state=row["state"],
                    country=row["country"],
                    climate_site=row["climate_site"],
                    wfo=row["wfo"],
                    tzname=row["tzname"],
                    ncdc81=row["ncdc81"],
                    ugc_county=row["ugc_county"],
                    ugc_zone=row["ugc_zone"],
                    county=row["county"],
                    sid=row["id"],
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
    network = form.getfirst("network", "KCCI")

    mckey = "/geojson/network/%s.geojson" % (network,)
    mc = memcache.Client(["iem-memcached:11211"], debug=0)
    res = mc.get(mckey)
    if not res:
        res = run(network)
        mc.set(mckey, res, 3600)

    if cb is None:
        ssw(res)
    else:
        ssw("%s(%s)" % (html_escape(cb), res))


if __name__ == "__main__":
    # Go Main Go
    main()
