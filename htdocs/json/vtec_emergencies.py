#!/usr/bin/env python
"""Listing of VTEC emergencies"""
import cgi
import json

import memcache
import psycopg2.extras
from pyiem.util import get_dbconn, ssw

ISO9660 = "%Y-%m-%dT%H:%M:%SZ"


def run():
    """Generate data."""
    pgconn = get_dbconn('postgis')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute("""
        SELECT extract(year from issue) as year, wfo, eventid,
        phenomena, significance,
        min(product_issue at time zone 'UTC') as utc_product_issue,
        min(init_expire at time zone 'UTC') as utc_init_expire,
        min(issue at time zone 'UTC') as utc_issue,
        max(expire at time zone 'UTC') as utc_expire from warnings
        WHERE phenomena in ('TO', 'FF') and significance = 'W'
        and is_emergency
        GROUP by year, wfo, eventid, phenomena, significance
        ORDER by utc_issue ASC
    """)
    res = {'events': []}
    for row in cursor:
        uri = "/vtec/#%s-O-NEW-K%s-%s-%s-%04i" % (
            row['year'], row['wfo'], row['phenomena'], row['significance'],
            row['eventid'])
        res['events'].append(
            dict(
                year=row['year'],
                phenomena=row['phenomena'],
                significance=row['significance'],
                eventid=row['eventid'],
                issue=row['utc_issue'].strftime(ISO9660),
                product_issue=row['utc_product_issue'].strftime(ISO9660),
                expire=row['utc_expire'].strftime(ISO9660),
                init_expire=row['utc_init_expire'].strftime(ISO9660),
                uri=uri,
                wfo=row['wfo']
                )
        )

    return json.dumps(res)


def main():
    """Main()"""
    ssw("Content-type: application/json\n\n")

    form = cgi.FieldStorage()
    cb = form.getfirst("callback", None)

    mckey = "/json/vtec_emergencies"
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    if not res:
        res = run()
        mc.set(mckey, res, 3600)

    if cb is None:
        ssw(res)
    else:
        ssw("%s(%s)" % (cgi.escape(cb, quote=True), res))


if __name__ == '__main__':
    main()
