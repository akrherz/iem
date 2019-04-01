#!/usr/bin/env python
"""
 Search for NWS Text, return JSON
"""
import cgi
import json
import datetime

import memcache
import pytz
from pyiem.util import get_dbconn, ssw


def run(sts, ets, awipsid):
    """ Actually do some work! """
    dbconn = get_dbconn('afos')
    cursor = dbconn.cursor()

    res = {'results': []}
    pillimit = "pil"
    if len(awipsid) == 3:
        pillimit = "substr(pil, 1, 3) "
    cursor.execute("""
    SELECT data,
    to_char(entered at time zone 'UTC', 'YYYY-MM-DDThh24:MIZ'),
    source, wmo from products WHERE
    entered >= %s and entered < %s and """ + pillimit + """ = %s
    ORDER by entered ASC
    """, (sts, ets, awipsid))
    for row in cursor:
        res['results'].append(dict(ttaaii=row[3],
                                   utcvalid=row[1],
                                   data=row[0],
                                   cccc=row[2]))
    return json.dumps(res)


def main():
    """ Do Stuff """
    ssw("Content-type: application/json\n\n")

    form = cgi.FieldStorage()
    awipsid = form.getfirst('awipsid')[:6]
    sts = form.getfirst('sts')
    ets = form.getfirst('ets')
    cb = form.getfirst('callback', None)

    mckey = "/json/nwstext_search/%s/%s/%s?callback=%s" % (sts, ets,
                                                           awipsid, cb)
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    if not res:
        sts = datetime.datetime.strptime(sts, '%Y-%m-%dT%H:%MZ')
        sts = sts.replace(tzinfo=pytz.utc)
        ets = datetime.datetime.strptime(ets, '%Y-%m-%dT%H:%MZ')
        ets = ets.replace(tzinfo=pytz.utc)
        now = datetime.datetime.utcnow()
        now = now.replace(tzinfo=pytz.utc)
        cacheexpire = 0 if ets < now else 120

        res = run(sts, ets, awipsid)
        mc.set(mckey, res, cacheexpire)

    if cb is None:
        ssw(res)
    else:
        ssw("%s(%s)" % (cgi.escape(cb, quote=True), res))


if __name__ == '__main__':
    main()
