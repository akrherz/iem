#!/usr/bin/env python
"""
Provide nws text in JSON format
"""
# stdlib
import cgi
import datetime
import json
import sys
# extras
import pytz
import psycopg2


def main():
    """Go Main"""
    pgconn = psycopg2.connect(database='afos', host='iemdb', user='nobody')
    acursor = pgconn.cursor()
    form = cgi.FieldStorage()
    pid = form.getvalue('product_id', '201302241937-KSLC-NOUS45-PNSSLC')
    cb = form.getvalue('callback', None)
    utc = datetime.datetime.strptime(pid[:12], '%Y%m%d%H%M')
    utc = utc.replace(tzinfo=pytz.timezone("UTC"))
    pil = pid[-6:]
    root = {'products': []}

    acursor.execute("""
        SELECT data from products where pil = %s and
        entered = %s
        """, (pil, utc))
    for row in acursor:
        root['products'].append({
                                 'data': row[0]
                                 })

    sys.stdout.write("Content-type: application/javascript\n\n")
    if cb is None:
        sys.stdout.write(json.dumps(root))
    else:
        sys.stdout.write("%s(%s)" % (cb, json.dumps(root)))


if __name__ == '__main__':
    main()
