#!/usr/bin/env python
""" Service to dump out IBW tags for a WFO / Year"""
import sys
import cgi
import json
import datetime

import psycopg2
import memcache


def ptime(val):
    """Pretty print a timestamp"""
    if val is None:
        return val
    return val.strftime("%Y-%m-%dT%H:%M:%SZ")


def run(wfo, year):
    """ Actually generate output """
    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
    cursor = pgconn.cursor()
    cursor.execute("""
    WITH stormbased as (
     SELECT eventid, phenomena, issue at time zone 'UTC' as utc_issue,
     expire at time zone 'UTC' as utc_expire,
     polygon_begin at time zone 'UTC' as utc_polygon_begin,
     polygon_end at time zone 'UTC' as utc_polygon_end,
     status, windtag, hailtag, tornadotag, tml_sknt, tornadodamagetag, wfo
     from sbw_""" + str(year) + """ WHERE wfo = %s
     and phenomena in ('SV', 'TO')
     and significance = 'W'    and status != 'EXP' and status != 'CAN'
 ),

 countybased as (
     select string_agg( u.name || ' ['||u.state||']', ', ') as locations,
     eventid, phenomena from warnings_""" + str(year) + """ w JOIN ugcs u
    ON (u.gid = w.gid) WHERE w.wfo = %s and
    significance = 'W' and phenomena in ('SV', 'TO')
    and eventid is not null GROUP by eventid, phenomena
 )

 SELECT c.eventid, c.locations, s.utc_issue, s.utc_expire,
 s.utc_polygon_begin, s.utc_polygon_end, s.status, s.windtag, s.hailtag,
 s.tornadotag, s.tml_sknt, s.tornadodamagetag, s.wfo, s.phenomena
 from countybased c, stormbased s WHERE c.eventid = s.eventid and
 c.phenomena = s.phenomena
 ORDER by eventid ASC, utc_polygon_begin ASC
     """, (wfo, wfo))

    res = dict(year=year, wfo=wfo, gentime=ptime(datetime.datetime.utcnow()),
               results=[])
    for row in cursor:
        data = dict(eventid=row[0], locations=row[1],
                    issue=ptime(row[2]), expire=ptime(row[3]),
                    polygon_begin=ptime(row[4]), polygon_end=ptime(row[5]),
                    status=row[6], windtag=row[7], hailtag=row[8],
                    tornadotag=row[9], tml_sknt=row[10],
                    tornadodamagetag=row[11],
                    wfo=row[12], phenomena=row[13])
        res['results'].append(data)

    return json.dumps(res)


def main():
    """ Go Main Go """
    sys.stdout.write("Content-type: application/json\n\n")
    form = cgi.FieldStorage()
    wfo = form.getfirst('wfo', 'DMX')[:4]
    year = int(form.getfirst('year', 2015))
    cb = form.getfirst('callback', None)

    mckey = "/json/ibw_tags/%s/%s" % (wfo, year)
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    if not res:
        res = run(wfo, year)
        mc.set(mckey, res, 86400)

    if cb is None:
        sys.stdout.write(res)
    else:
        sys.stdout.write("%s(%s)" % (cb, res))


if __name__ == '__main__':
    main()
