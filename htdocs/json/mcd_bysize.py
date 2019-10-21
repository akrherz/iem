#!/usr/bin/env python
"""SPC MCD service."""
import cgi
import json

from pyiem.util import get_dbconn, ssw

ISO9660 = '%Y-%m-%dT%H:%MZ'


def dowork(count, sort):
    """ Actually do stuff"""
    pgconn = get_dbconn('postgis')
    cursor = pgconn.cursor()

    res = dict(mcds=[])

    cursor.execute("""
        SELECT issue at time zone 'UTC' as i,
        expire at time zone 'UTC' as e,
        num,
        product_id, year,
        ST_Area(geom::geography) / 1000000. as area_sqkm
        from mcd WHERE not ST_isEmpty(geom)
        ORDER by area_sqkm """ + sort + """ LIMIT %s
    """, (count, ))
    for row in cursor:
        url = ("https://www.spc.noaa.gov/products/md/%s/md%04i.html"
               ) % (row[4], row[2])
        res['mcds'].append(
            dict(spcurl=url,
                 year=row[4],
                 utc_issue=row[0].strftime(ISO9660),
                 utc_expire=row[1].strftime(ISO9660),
                 product_num=row[2],
                 product_id=row[3],
                 area_sqkm=row[5]))

    return json.dumps(res)


def main():
    """Do Main Stuff"""
    ssw("Content-type: application/vnd.geo+json\n\n")

    form = cgi.FieldStorage()
    count = int(form.getfirst('count', 10))
    sort = form.getfirst('sort', 'DESC').upper()
    if sort not in ['ASC', 'DESC']:
        return

    cb = form.getfirst('callback', None)

    res = dowork(count, sort)
    if cb is None:
        ssw(res)
    else:
        ssw("%s(%s)" % (cgi.escape(cb, quote=True), res))


if __name__ == '__main__':
    main()
