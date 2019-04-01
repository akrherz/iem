#!/usr/bin/env python
"""SPC MCD service
"""
import os
import cgi
import json

import memcache
from pyiem.util import get_dbconn, ssw

ISO9660 = '%Y-%m-%dT%H:%MZ'


def dowork(lon, lat):
    """ Actually do stuff"""
    pgconn = get_dbconn('postgis')
    cursor = pgconn.cursor()

    res = dict(mcds=[])

    cursor.execute("""
    SELECT issue at time zone 'UTC' as i,
    expire at time zone 'UTC' as e,
    product_num,
    product_id
    from text_products WHERE pil = 'SWOMCD'
    and ST_Contains(geom, ST_GeomFromEWKT('SRID=4326;POINT(%s %s)'))
    ORDER by product_id DESC
    """, (lon, lat))
    for row in cursor:
        url = ("http://www.spc.noaa.gov/products/md/%s/md%04i.html"
               ) % (row[3][:4], row[2])
        res['mcds'].append(
            dict(spcurl=url,
                 year=row[0].year,
                 utc_issue=row[0].strftime(ISO9660),
                 utc_expire=row[1].strftime(ISO9660),
                 product_num=row[2],
                 product_id=row[3]))

    return json.dumps(res)


def main():
    """Do Main Stuff"""
    ssw("Content-type: application/vnd.geo+json\n\n")

    form = cgi.FieldStorage()
    lat = float(form.getfirst('lat', 42.0))
    lon = float(form.getfirst('lon', -95.0))

    cb = form.getfirst('callback', None)

    hostname = os.environ.get("SERVER_NAME", "")
    mckey = ("/json/spcmcd/%.4f/%.4f"
             ) % (lon, lat)
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey) if hostname != 'iem.local' else None
    if not res:
        res = dowork(lon, lat)
        mc.set(mckey, res, 3600)

    if cb is None:
        ssw(res)
    else:
        ssw("%s(%s)" % (cgi.escape(cb, quote=True), res))


if __name__ == '__main__':
    main()
