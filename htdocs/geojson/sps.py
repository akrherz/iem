#!/usr/bin/env python
""" Generate a GeoJSON of current SPS Polygons """
import cgi
import json
import datetime

import memcache
import psycopg2.extras
from pyiem.util import get_dbconn, ssw


def run():
    """ Actually do the hard work of getting the current SPS in geojson """
    pgconn = get_dbconn('postgis')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    utcnow = datetime.datetime.utcnow()

    # Look for polygons into the future as well as we now have Flood products
    # with a start time in the future
    cursor.execute("""
        SELECT ST_asGeoJson(geom) as geojson, product_id,
        issue at time zone 'UTC' as utc_issue,
        expire at time zone 'UTC' as utc_expire
        from text_products WHERE issue < now() and expire > now()
        and not ST_IsEmpty(geom) and geom is not null and
        substr(product_id,26, 3) = 'SPS'
    """)

    res = {'type': 'FeatureCollection',
           'features': [],
           'generation_time': utcnow.strftime("%Y-%m-%dT%H:%M:%SZ"),
           'count': cursor.rowcount}
    for row in cursor:
        sts = row['utc_issue'].strftime("%Y-%m-%dT%H:%M:%SZ")
        ets = row['utc_expire'].strftime("%Y-%m-%dT%H:%M:%SZ")
        href = "/api/1/nwstext.txt?pid=%s" % (row['product_id'], )
        res['features'].append(dict(type="Feature",
                                    id=row['product_id'],
                                    properties=dict(
                                        href=href,
                                        issue=sts,
                                        expire=ets),
                                    geometry=json.loads(row['geojson'])
                                    ))

    return json.dumps(res)


def main():
    """Do Main"""
    ssw("Content-type: application/vnd.geo+json\n\n")

    form = cgi.FieldStorage()
    cb = form.getfirst('callback', None)

    mckey = "/geojson/sps.geojson"
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    if not res:
        res = run()
        mc.set(mckey, res, 15)

    if cb is None:
        ssw(res)
    else:
        ssw("%s(%s)" % (cgi.escape(cb, quote=True), res))


if __name__ == '__main__':
    main()
