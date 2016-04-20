#!/usr/bin/env python
""" Generate a GeoJSON of current storm based warnings """
import memcache
import sys
import cgi


def run():
    """ Actually do the hard work of getting the current SBW in geojson """
    import json
    import psycopg2.extras
    import datetime

    pgconn = psycopg2.connect(database='mesosite', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    utcnow = datetime.datetime.utcnow()

    # Look for polygons into the future as well as we now have Flood products
    # with a start time in the future
    cursor.execute("""
        SELECT ST_asGeoJson(extent) as geojson, id, name
        from networks WHERE extent is not null ORDER by id ASC
    """)

    res = {'type': 'FeatureCollection',
           'crs': {'type': 'EPSG',
                   'properties': {'code': 4326, 'coordinate_order': [1, 0]}},
           'features': [],
           'generation_time': utcnow.strftime("%Y-%m-%dT%H:%M:%SZ"),
           'count': cursor.rowcount}
    for row in cursor:
        res['features'].append(dict(type="Feature",
                                    id=row['id'],
                                    properties=dict(
                                        name=row['name']),
                                    geometry=json.loads(row['geojson'])
                                    ))

    return json.dumps(res)


def main():
    """Do Something"""
    # Go Main Go
    sys.stdout.write("Content-type: application/vnd.geo+json\n\n")

    form = cgi.FieldStorage()
    cb = form.getfirst('callback', None)

    mckey = "/geojson/network.geojson"
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    if not res:
        res = run()
        mc.set(mckey, res, 86400)

    if cb is None:
        sys.stdout.write(res)
    else:
        sys.stdout.write("%s(%s)" % (cb, res))

if __name__ == '__main__':
    main()
