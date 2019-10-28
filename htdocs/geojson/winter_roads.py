#!/usr/bin/env python
""" Generate a GeoJSON of current storm based warnings """
import cgi
import json
import datetime

import memcache
from pyiem.util import get_dbconn, ssw, html_escape


def run():
    """ Actually do the hard work of getting the current SBW in geojson """
    utcnow = datetime.datetime.utcnow()
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()

    # Look for polygons into the future as well as we now have Flood products
    # with a start time in the future
    cursor.execute(
        """
        SELECT ST_asGeoJson(ST_Transform(simple_geom, 4326)) as geojson,
        cond_code, c.segid from
        roads_current c JOIN roads_base b on (c.segid = b.segid)
        WHERE c.valid > now() - '1000 hours'::interval
        and cond_code is not null
    """
    )

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
                id=row[2],
                properties=dict(code=row[1]),
                geometry=json.loads(row[0]),
            )
        )

    return json.dumps(res)


def main():
    """Main Workflow"""
    ssw("Content-type: application/vnd.geo+json\n\n")

    form = cgi.FieldStorage()
    cb = form.getfirst("callback", None)

    mckey = "/geojson/winter_roads.geojson"
    mc = memcache.Client(["iem-memcached:11211"], debug=0)
    res = mc.get(mckey)
    if not res:
        res = run()
        mc.set(mckey, res, 120)

    if cb is None:
        ssw(res)
    else:
        ssw("%s(%s)" % (html_escape(cb), res))


if __name__ == "__main__":
    main()
