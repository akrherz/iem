#!/usr/bin/env python
""" Generate a GeoJSON of current SPS Polygons """
import memcache
import sys
import cgi


def run():
    """ Actually do the hard work of getting the current SPS in geojson """
    import json
    import psycopg2.extras
    import datetime

    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    utcnow = datetime.datetime.utcnow()

    # Look for polygons into the future as well as we now have Flood products
    # with a start time in the future
    cursor.execute("""
        SELECT ST_asGeoJson(geom) as geojson,
        issue at time zone 'UTC' as utc_issue,
        expire at time zone 'UTC' as utc_expire
        from text_products WHERE issue < now() and expire > now()
        and not ST_IsEmpty(geom) and geom is not null
    """)

    res = {'type': 'FeatureCollection',
           'crs': {'type': 'EPSG',
                   'properties': {'code': 4326, 'coordinate_order': [1, 0]}},
           'features': [],
           'generation_time': utcnow.strftime("%Y-%m-%dT%H:%M:%SZ"),
           'count': cursor.rowcount}
    for i, row in enumerate(cursor):
        sts = row['utc_issue'].strftime("%Y-%m-%dT%H:%M:%SZ")
        ets = row['utc_expire'].strftime("%Y-%m-%dT%H:%M:%SZ")
        res['features'].append(dict(type="Feature",
                                    id=i,
                                    properties=dict(
                                        issue=sts,
                                        expire=ets),
                                    geometry=json.loads(row['geojson'])
                                    ))

    return json.dumps(res)


if __name__ == '__main__':
    # Go Main Go
    sys.stdout.write("Content-type: application/vnd.geo+json\n\n")

    form = cgi.FieldStorage()
    cb = form.getfirst('callback', None)

    mckey = "/geojson/sps.geojson"
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    if not res:
        res = run()
        mc.set(mckey, res, 15)

    if cb is None:
        sys.stdout.write(res)
    else:
        sys.stdout.write("%s(%s)" % (cb, res))
