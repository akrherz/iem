#!/usr/bin/env python
"""VTEC event metadata"""
import cgi
import json
import datetime

import memcache
import psycopg2.extras
from pyiem.util import get_dbconn, ssw

ISO9660 = "%Y-%m-%dT%H:%M:%SZ"


def run(wfo, year, phenomena, significance, etn):
    """Do great things"""
    pgconn = get_dbconn('postgis')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    table = "warnings_%s" % (year,)
    # This is really a BUG here and we need to rearch the database
    cursor.execute("""
    SELECT
    first_value(report) OVER (ORDER by product_issue ASC) as report,
    first_value(svs) OVER (ORDER by product_issue ASC) as svs_updates,
    first_value(issue at time zone 'UTC')
        OVER (ORDER by issue ASC NULLS LAST) as utc_issue,
    first_value(expire at time zone 'UTC')
        OVER (ORDER by expire DESC NULLS LAST) as utc_expire
    from """+table+""" w
    WHERE w.wfo = %s and eventid = %s and
    phenomena = %s and significance = %s
    """, (wfo, etn, phenomena, significance))
    res = {
        'generation_time': datetime.datetime.utcnow().strftime(ISO9660),
        'year': year,
        'phenomena': phenomena,
        'significance': significance,
        'etn': etn,
        'wfo': wfo
        }
    if cursor.rowcount == 0:
        return json.dumps(res)

    row = cursor.fetchone()
    res['report'] = {'text': row['report']}
    res['svs'] = []
    if row['svs_updates'] is not None:
        for token in row['svs_updates'].split("__"):
            if token.strip() != '':
                res['svs'].append({'text': token})
    res['utc_issue'] = row['utc_issue'].strftime(ISO9660)
    res['utc_expire'] = row['utc_expire'].strftime(ISO9660)

    # Now lets get UGC information
    cursor.execute("""
    SELECT
    u.ugc,
    u.name,
    w.status,
    w.product_issue at time zone 'UTC' utc_product_issue,
    w.issue at time zone 'UTC' utc_issue,
    w.expire at time zone 'UTC' utc_expire,
    w.init_expire at time zone 'UTC' utc_init_expire,
    w.updated at time zone 'UTC' utc_updated
    from """+table+""" w JOIN ugcs u on (w.gid = u.gid)
    WHERE w.wfo = %s and eventid = %s and
    phenomena = %s and significance = %s
    ORDER by u.ugc ASC
    """, (wfo, etn, phenomena, significance))
    res['ugcs'] = []
    for row in cursor:
        res['ugcs'].append({
            'ugc': row['ugc'],
            'name': row['name'],
            'status': row['status'],
            'utc_product_issue': row['utc_product_issue'].strftime(ISO9660),
            'utc_issue': row['utc_issue'].strftime(ISO9660),
            'utc_init_expire': row['utc_init_expire'].strftime(ISO9660),
            'utc_expire': row['utc_expire'].strftime(ISO9660),
            'utc_updated': row['utc_updated'].strftime(ISO9660),
            })

    return json.dumps(res)


def main():
    """Main()"""
    ssw("Content-type: application/vnd.geo+json\n\n")

    form = cgi.FieldStorage()
    wfo = form.getfirst("wfo", "MPX")
    if len(wfo) == 4:
        wfo = wfo[1:]
    year = int(form.getfirst("year", 2015))
    phenomena = form.getfirst('phenomena', 'SV')[:2]
    significance = form.getfirst('significance', 'W')[:1]
    etn = int(form.getfirst('etn', 1))
    cb = form.getfirst("callback", None)

    mckey = "/json/vtec_event/%s/%s/%s/%s/%s" % (wfo, year, phenomena,
                                                 significance, etn)
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    if not res:
        res = run(wfo, year, phenomena, significance, etn)
        mc.set(mckey, res, 300)

    if cb is None:
        ssw(res)
    else:
        ssw("%s(%s)" % (cgi.escape(cb, quote=True), res))


if __name__ == '__main__':
    main()
