#!/usr/bin/env python
""" Find VTEC events by a given Lat / Lon pair """
import cgi
import sys
import json
import datetime


def run(lon, lat, sdate, edate):
    """Generate a report of VTEC ETNs used for a WFO and year

    Args:
      wfo (str): 3 character WFO identifier
      year (int): year to run for
    """
    import psycopg2
    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
    cursor = pgconn.cursor()

    cursor.execute("""
    WITH myugcs as (
        select gid from ugcs where
        ST_Contains(geom, ST_SetSRID(ST_GeomFromEWKT('POINT(%s %s)'),4326))
    )
    SELECT
    to_char(issue at time zone 'UTC', 'YYYY-MM-DDThh24:MI:SSZ') as iso_issued,
 to_char(expire at time zone 'UTC', 'YYYY-MM-DDThh24:MI:SSZ') as iso_expired,
    eventid, phenomena, significance, wfo
    from warnings w JOIN myugcs u on (w.gid = u.gid) WHERE
    issue > %s and issue < %s ORDER by issue ASC
    """, (lon, lat, sdate, edate))

    res = {'events': []}
    for row in cursor:
        res['events'].append({'issue': row[0],
                              'expire': row[1],
                              'eventid': row[2],
                              'phenomena': row[3],
                              'significance': row[4],
                              'wfo': row[5]})

    return json.dumps(res)


def main():
    """Main()"""
    sys.stdout.write("Content-type: application/json\n\n")

    form = cgi.FieldStorage()
    lat = float(form.getfirst("lat", 42.5))
    lon = float(form.getfirst("lon", -95.5))
    sdate = datetime.datetime.strptime(form.getfirst("sdate", "1986/1/1"),
                                       "%Y/%m/%d")
    edate = datetime.datetime.strptime(form.getfirst("edate", "2099/1/1"),
                                       "%Y/%m/%d")
    cb = form.getfirst('callback', None)

    res = run(lon, lat, sdate, edate)
    if cb is None:
        sys.stdout.write(res)
    else:
        sys.stdout.write("%s(%s)" % (cb, res))


if __name__ == '__main__':
    main()
