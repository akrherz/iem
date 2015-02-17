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

    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    utcnow = datetime.datetime.utcnow()
    sbwtable = "sbw_%s" % (utcnow.year,)

    # Look for polygons into the future as well as we now have Flood products
    # with a start time in the future
    cursor.execute("""
        SELECT ST_asGeoJson(geom) as geojson, phenomena, eventid, wfo,
        significance, polygon_end
        from """+sbwtable+""" WHERE
        polygon_begin <= (now() + '7 days'::interval) and
        polygon_end > now()
    """)

    res = {'type': 'FeatureCollection',
           'crs': {'type': 'EPSG',
                   'properties': {'code': 4326, 'coordinate_order': [1, 0]}},
           'features': [],
           'generation_time': utcnow.strftime("%Y-%m-%dT%H:%M:%SZ"),
           'count': cursor.rowcount}
    for row in cursor:
        sid = "%(wfo)s.%(phenomena)s.%(significance)s.%(eventid)04i" % row
        ets = row['polygon_end'].strftime("%Y-%m-%dT%H:%M:%SZ")
        res['features'].append(dict(type="Feature",
                                    id=sid,
                                    properties=dict(
                                        phenomena=row['phenomena'],
                                        significance=row['significance'],
                                        wfo=row['wfo'],
                                        eventid=row['eventid'],
                                        expire=ets),
                                    geometry=json.loads(row['geojson'])
                                    ))

    return json.dumps(res)


if __name__ == '__main__':
    # Go Main Go
    sys.stdout.write("Content-type: application/vnd.geo+json\n\n")

    form = cgi.FieldStorage()
    cb = form.getfirst('callback', None)

    mckey = "/geojson/sbw.geojson"
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    if not res:
        res = run()
        mc.set(mckey, res, 15)

    if cb is None:
        sys.stdout.write(res)
    else:
        sys.stdout.write("%s(%s)" % (cb, res))
