#!/usr/bin/env python
"""
 Return NWS Text
"""
import cgi
import sys
import datetime

import psycopg2
import pytz
import memcache


def get_data(product):
    """ Go get this product from the database
    201410071957-KDMX-FXUS63-AFDDMX
    """
    pgconn = psycopg2.connect(database='afos', host='iemdb', user='nobody')
    cursor = pgconn.cursor()

    ts = datetime.datetime.strptime(product[:12], "%Y%m%d%H%M")
    ts = ts.replace(tzinfo=pytz.timezone("UTC"))

    source = product[13:17]
    pil = product[25:]

    cursor.execute("""SELECT data from products where source = %s
    and pil = %s and entered = %s""", (source, pil, ts))

    if cursor.rowcount == 0:
        return 'Not Found %s %s' % (source, pil)

    row = cursor.fetchone()
    return row[0].replace("\r\r\n", "\n")


def main():
    ''' Do Stuff '''
    sys.stdout.write("Content-type: text/plain\n\n")
    field = cgi.FieldStorage()
    product = field.getfirst('p', None)[:31]
    cb = field.getfirst('callback', None)

    mckey = "/api/nwstext/%s" % (product,)
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    if not res:
        res = get_data(product)
        mc.set(mckey, res, 1800)
    if cb is None:
        sys.stdout.write(res)
    else:
        sys.stdout.write("%s(%s)" % (cb, res))


if __name__ == '__main__':
    main()
