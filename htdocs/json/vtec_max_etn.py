#!/usr/bin/env python
"""Show Max ETNs by wfo, phenomena, sig, by year"""
import cgi
import datetime
import sys
import json

import memcache
import pandas as pd
from pyiem.util import get_dbconn


def run(year, fmt):
    """Generate a report of max VTEC ETNs

    Args:
      year (int): year to run for
    """
    pgconn = get_dbconn('postgis')
    cursor = pgconn.cursor()
    utcnow = datetime.datetime.utcnow()

    table = "warnings_%s" % (year,)
    cursor.execute("""
    SELECT wfo, phenomena, significance, max(eventid) from
    """+table+""" WHERE wfo is not null and eventid is not null and
    phenomena is not null and significance is not null
    GROUP by wfo, phenomena, significance
    ORDER by wfo ASC, phenomena ASC, significance ASC
    """)
    res = {'count': cursor.rowcount,
           'generated_at': utcnow.strftime("%Y-%m-%dT%H:%M:%SZ"),
           'columns': [
                {'name': 'wfo', 'type': 'str'},
                {'name': 'phenomena', 'type': 'str'},
                {'name': 'significance', 'type': 'str'},
                {'name': 'max_eventid', 'type': 'int'}
                ], 'table': cursor.fetchall()}

    if fmt == 'json':
        return json.dumps(res)
    if not res['table']:
        return "NO DATA"
    # Make a hacky table
    df = pd.DataFrame(res['table'],
                      columns=[c['name'] for c in res['columns']])
    df = df.pivot_table(index='wfo', columns=['phenomena', 'significance'],
                        values='max_eventid')
    df.fillna("", inplace=True)

    html = ("<p><strong>Table generated at: %s</strong></p>\n%s"
            ) % (res['generated_at'],
                 df.style.set_table_attributes(' class="iemdt"').render())
    return html


def main():
    """Main()"""

    form = cgi.FieldStorage()
    year = int(form.getfirst("year", 2015))
    fmt = form.getfirst('format', 'json')
    if fmt not in ['json', 'html']:
        return
    cb = form.getfirst("callback", None)
    if fmt == 'json':
        sys.stdout.write("Content-type: application/json\n\n")
    else:
        sys.stdout.write("Content-type: text/html\n\n")

    mckey = "/json/vtec_max_etn/%s/%s" % (year, fmt)
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    if res is None:
        res = run(year, fmt)
        mc.set(mckey, res, 3600)

    if cb is None:
        sys.stdout.write(res)
    else:
        sys.stdout.write("%s(%s)" % (cb, res))


if __name__ == '__main__':
    main()
