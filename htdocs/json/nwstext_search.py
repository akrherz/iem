#!/usr/bin/env python
"""
 Search for NWS Text, return JSON
"""
import memcache
import cgi
import sys
import datetime
import pytz
import json


def run(sts, ets, awipsid):
    """ Actually do some work! """
    import psycopg2

    dbconn = psycopg2.connect(database='afos', host='iemdb', user='nobody')
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
    sys.stdout.write("Content-type: application/json\n\n")

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
        sts = sts.replace(tzinfo=pytz.timezone("UTC"))
        ets = datetime.datetime.strptime(ets, '%Y-%m-%dT%H:%MZ')
        ets = ets.replace(tzinfo=pytz.timezone("UTC"))
        now = datetime.datetime.utcnow()
        now = now.replace(tzinfo=pytz.timezone("UTC"))
        cacheexpire = 0 if ets < now else 120

        res = run(sts, ets, awipsid)
        mc.set(mckey, res, cacheexpire)

    if cb is None:
        sys.stdout.write(res)
    else:
        sys.stdout.write("%s(%s)" % (cb, res))


if __name__ == '__main__':
    main()
