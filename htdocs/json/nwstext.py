#!/usr/bin/env python
"""
Provide nws text in JSON format
"""
# stdlib
import cgi
import datetime
import json
# extras
import pytz
from pyiem.util import get_dbconn, ssw


def main():
    """Go Main"""
    pgconn = get_dbconn('afos')
    acursor = pgconn.cursor()
    form = cgi.FieldStorage()
    pid = form.getvalue('product_id', '201302241937-KSLC-NOUS45-PNSSLC')
    cb = form.getvalue('callback', None)
    utc = datetime.datetime.strptime(pid[:12], '%Y%m%d%H%M')
    utc = utc.replace(tzinfo=pytz.utc)
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

    ssw("Content-type: application/javascript\n\n")
    if cb is None:
        ssw(json.dumps(root))
    else:
        ssw("%s(%s)" % (cgi.escape(cb, quote=True), json.dumps(root)))


if __name__ == '__main__':
    main()
