#!/usr/bin/env python
"""SPC Outlook JSON service
"""
import os
import cgi
import json
import sys
import memcache
import psycopg2


def dowork(lon, lat, last, day, cat):
    """ Actually do stuff"""
    postgis = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
    cursor = postgis.cursor()

    res = dict(outlooks=[])

    cursor.execute("""
    WITH data as (
        SELECT issue at time zone 'UTC' as i,
        expire at time zone 'UTC' as e,
        valid at time zone 'UTC' as v,
        threshold, category,
        rank() OVER (PARTITION by expire ORDER by issue ASC)
        from spc_outlooks where
        ST_Contains(geom, ST_GeomFromEWKT('SRID=4326;POINT(%s %s)'))
        and day = %s and outlook_type = 'C' and category = %s
        and threshold not in ('TSTM') ORDER by issue DESC)
    SELECT i, e, v, threshold, category from data where rank = 1
    ORDER by e DESC
    """, (lon, lat, day, cat))
    running = {}
    for row in cursor:
        if last > 0:
            running.setdefault(row[3], 0)
            running[row[3]] += 1
            if running[row[3]] > last:
                continue
        res['outlooks'].append(
            dict(day=day,
                 utc_issue=row[0].strftime("%Y-%m-%dT%H:%M:%SZ"),
                 utc_expire=row[1].strftime("%Y-%m-%dT%H:%M:%SZ"),
                 utc_valid=row[2].strftime("%Y-%m-%dT%H:%M:%SZ"),
                 threshold=row[3],
                 category=row[4]))

    postgis.close()

    return json.dumps(res)


def main():
    """Do Main Stuff"""
    sys.stdout.write("Content-type: application/vnd.geo+json\n\n")

    form = cgi.FieldStorage()
    lat = float(form.getfirst('lat', 42.0))
    lon = float(form.getfirst('lon', -95.0))
    last = int(form.getfirst('last', 0))
    day = int(form.getfirst('day', 1))
    cat = form.getfirst('cat', 'categorical').upper()

    cb = form.getfirst('callback', None)

    hostname = os.environ.get("SERVER_NAME", "")
    mckey = "/json/spcoutlook/%.4f/%.4f/%s/%s/%s" % (lon, lat, last, day, cat)
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey) if hostname != 'iem.local' else None
    if not res:
        res = dowork(lon, lat, last, day, cat)
        mc.set(mckey, res, 3600)

    if cb is None:
        sys.stdout.write(res)
    else:
        sys.stdout.write("%s(%s)" % (cb, res))


if __name__ == '__main__':
    main()
