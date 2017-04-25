#!/usr/bin/env python
"""Listing of VTEC events for a WFO and year"""
import cgi
import sys
import json
import memcache


def run(wfo, year):
    """Generate a report of VTEC ETNs used for a WFO and year

    Args:
      wfo (str): 3 character WFO identifier
      year (int): year to run for
    """
    import psycopg2
    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
    cursor = pgconn.cursor()

    table = "warnings_%s" % (year,)
    cursor.execute("""
    SELECT distinct phenomena, significance, eventid,
    issue at time zone 'UTC' as utc_issue,
    init_expire at time zone 'UTC' as utc_expire from
    """+table+""" WHERE wfo = %s and eventid is not null and
    phenomena is not null and significance is not null
    ORDER by phenomena ASC, significance ASC, utc_issue ASC
    """, (wfo,))
    lastrow = [None]*5
    res = {'wfo': wfo, 'year': year, 'events': []}
    for row in cursor:
        if (row[0] == lastrow[0] and row[1] == lastrow[1] and
                row[2] == lastrow[2] and
                (row[3] == lastrow[3] or row[4] == lastrow[4])):
            pass
        else:
            issue = None
            expire = None
            if row[3] is not None:
                issue = row[3].strftime("%Y-%m-%dT%H:%M:%SZ")
            if row[4] is not None:
                expire = row[4].strftime("%Y-%m-%dT%H:%M:%SZ")
            uri = "/vtec/#%s-O-NEW-K%s-%s-%s-%04i" % (year, wfo, row[0],
                                                      row[1], row[2])
            res['events'].append(dict(phenomena=row[0], significance=row[1],
                                      eventid=row[2], issue=issue,
                                      expire=expire, uri=uri))
        lastrow = row

    return json.dumps(res)


def main():
    """Main()"""
    sys.stdout.write("Content-type: application/json\n\n")

    form = cgi.FieldStorage()
    wfo = form.getfirst("wfo", "MPX")
    if len(wfo) == 4:
        wfo = wfo[1:]
    year = int(form.getfirst("year", 2015))
    cb = form.getfirst("callback", None)

    mckey = "/json/vtec_events/%s/%s" % (wfo, year)
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    if not res:
        res = run(wfo, year)
        mc.set(mckey, res, 3600)

    if cb is None:
        sys.stdout.write(res)
    else:
        sys.stdout.write("%s(%s)" % (cb, res))


if __name__ == '__main__':
    main()
