#!/usr/bin/env python
"""
Get storm based warnings by lat lon point
"""
import cgi
import psycopg2
import json
import sys


def get_events(lon, lat):
    """ Get Events """
    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
    cursor = pgconn.cursor()
    cursor.execute("""SET TIME ZONE 'UTC'""")
    cursor.execute("""
  select wfo, significance, phenomena, issue, expire, eventid from sbw
  where status = 'NEW' and
  ST_Contains(geom, ST_SetSRID(ST_GeomFromText('POINT(%s %s)'),4326))
  and phenomena in ('SV', 'TO', 'FF', 'FL', 'MA', 'FA') and
  issue > '2005-10-01'
  ORDER by issue ASC
    """, (lon, lat))
    data = {'sbws': []}
    for row in cursor:
        data['sbws'].append({
                             'phenomena': row[2], 'eventid': row[5],
                             'significance': row[1], 'wfo': row[0],
                             'issue': row[3].strftime("%Y-%m-%dT%H:%MZ"),
                             'expire': row[4].strftime("%Y-%m-%dT%H:%MZ")
                             })
    return data


def main():
    """ Go Main Go"""
    form = cgi.FieldStorage()
    lat = float(form.getfirst("lat"))
    lon = float(form.getfirst("lon"))

    data = get_events(lon, lat)
    sys.stdout.write("Content-type: application/json\n\n")
    sys.stdout.write(json.dumps(data))

if __name__ == '__main__':
    main()
