#!/usr/bin/env python
""" Generate a GeoJSON of US Drought Monitor"""
import sys
import cgi
import json
import datetime

import memcache
import psycopg2.extras
from pyiem.util import get_dbconn


def run(ts):
    """ Actually do the hard work of getting the USDM in geojson """
    pgconn = get_dbconn('postgis')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if ts == '':
        # Go get the latest USDM stored in the database!
        cursor.execute("""SELECT max(valid) from usdm""")
        ts = cursor.fetchone()[0]
    else:
        ts = datetime.datetime.strptime(ts, '%Y-%m-%d').date()
    offset = (ts.weekday() - 1) % 7
    tuesday = ts - datetime.timedelta(days=offset)

    # Look for polygons into the future as well as we now have Flood products
    # with a start time in the future
    cursor.execute("""
        SELECT ST_asGeoJson(geom) as geojson, dm, valid
        from usdm WHERE valid = %s ORDER by dm ASC
    """, (tuesday, ))

    utcnow = datetime.datetime.utcnow()
    res = {'type': 'FeatureCollection',
           'crs': {'type': 'EPSG',
                   'properties': {'code': 4326, 'coordinate_order': [1, 0]}},
           'features': [],
           'generation_time': utcnow.strftime("%Y-%m-%dT%H:%M:%SZ"),
           'count': cursor.rowcount}
    for row in cursor:
        res['features'].append(dict(type="Feature",
                                    id=row['dm'],
                                    properties=dict(
                                        date=row['valid'].strftime("%Y-%m-%d"),
                                        dm=row['dm']),
                                    geometry=json.loads(row['geojson'])
                                    ))

    return json.dumps(res)


def main():
    """Main Workflow"""
    sys.stdout.write("Content-type: application/vnd.geo+json\n\n")

    form = cgi.FieldStorage()
    cb = form.getfirst('callback', None)
    ts = form.getfirst('date', '')

    mckey = "/geojson/usdm.geojson|%s" % (ts,)
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    if not res:
        res = run(ts)
        mc.set(mckey, res, 15 if ts == '' else 3600)

    if cb is None:
        sys.stdout.write(res)
    else:
        sys.stdout.write("%s(%s)" % (cb, res))


if __name__ == '__main__':
    # Go Main Go
    main()
