#!/usr/bin/env python
"""Provide time series of USDM for a point"""
import sys
import cgi
import json
import datetime

import memcache
from pyiem.util import get_dbconn

ISO = "%Y-%m-%dT%H:%M:%SZ"


def make_date(val, default):
    """Convert the value into a date please"""
    if val == '':
        return default
    return datetime.datetime.strptime(val, '%Y-%m-%d')


def run(sdate, edate, lon, lat):
    """Do what we need to do!"""
    pgconn = get_dbconn('postgis')
    cursor = pgconn.cursor()
    sdate = make_date(sdate, datetime.date(2000, 1, 1))
    edate = make_date(edate, datetime.date(2050, 1, 1))

    cursor.execute("""
        SELECT to_char(valid, 'YYYY-MM-DD') as date, max(dm) from usdm WHERE
        ST_Contains(geom, ST_SetSRID(ST_GeomFromEWKT('POINT(%s %s)'),4326))
        and valid >= %s and valid <= %s
        GROUP by date ORDER by date ASC
    """, (lon, lat, sdate, edate))

    res = {'count': cursor.rowcount,
           'generated_at': datetime.datetime.utcnow().strftime(ISO),
           'columns': [
                {'name': 'valid', 'type': 'date'},
                {'name': 'category', 'type': 'int'},
                ], 'table': cursor.fetchall()}

    return json.dumps(res)


def main():
    """Main Workflow"""
    sys.stdout.write("Content-type: application/vnd.geo+json\n\n")

    form = cgi.FieldStorage()
    cb = form.getfirst('callback', None)
    sdate = form.getfirst('sdate', '')
    edate = form.getfirst('edate', '')
    lat = float(form.getfirst('lat', 42.0))
    lon = float(form.getfirst('lon', -95.))

    mckey = "/json/usdm/%s/%s/%.2f/%.2f" % (sdate, edate, lon, lat)
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    if not res:
        res = run(sdate, edate, lon, lat)
        mc.set(mckey, res, 3600)

    if cb is None:
        sys.stdout.write(res)
    else:
        sys.stdout.write("%s(%s)" % (cb, res))


if __name__ == '__main__':
    main()
