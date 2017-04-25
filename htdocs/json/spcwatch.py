#!/usr/bin/env python
"""
 Return GeoJSON of valid watches for a provided timestamp or just now
"""
import datetime
import cgi
import sys
import json
import memcache
import pytz


def dowork(valid):
    """Actually do stuff"""
    import psycopg2
    postgis = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
    cursor = postgis.cursor()

    res = dict(type='FeatureCollection',
               crs=dict(type='EPSG',
                        properties=dict(code=4326, coordinate_order=[1, 0])),
               features=[])

    cursor.execute("""
    SELECT sel, issued at time zone 'UTC', expired at time zone 'UTC', type,
    ST_AsGeoJSON(geom), num from watches where issued <= %s and
    expired > %s
    """, (valid, valid))
    for row in cursor:
        res['features'].append(
            dict(type='Feature', id=row[5],
                 properties=dict(
                                type=row[3],
                                number=row[5],
                                issue=row[1].strftime("%Y-%m-%dT%H:%M:%SZ"),
                                expire=row[2].strftime("%Y-%m-%dT%H:%M:%SZ")),
                 geometry=json.loads(row[4])))

    postgis.close()

    return json.dumps(res)


def main():
    """Main Workflow"""
    sys.stdout.write("Content-type: application/vnd.geo+json\n\n")

    form = cgi.FieldStorage()
    ts = form.getfirst('ts', None)
    if ts is None:
        ts = datetime.datetime.utcnow()
    else:
        ts = datetime.datetime.strptime(ts, '%Y%m%d%H%M')
    ts = ts.replace(tzinfo=pytz.timezone("UTC"))

    cb = form.getfirst('callback', None)

    mckey = "/json/spcwatch/%s?callback=%s" % (ts.strftime("%Y%m%d%H%M"), cb)
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    if not res:
        res = dowork(ts)
        mc.set(mckey, res)

    if cb is None:
        sys.stdout.write(res)
    else:
        sys.stdout.write("%s(%s)" % (cb, res))


if __name__ == '__main__':
    main()
