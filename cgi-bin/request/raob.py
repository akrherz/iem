#!/usr/bin/env python
"""
Download interface for data from RAOB network
"""
import cgi
import sys
import datetime

import pytz
from pyiem.util import get_dbconn
from pyiem.network import Table as NetworkTable


def m(val):
    """Helper"""
    if val is None:
        return 'M'
    return val


def fetcher(station, sts, ets):
    dbconn = get_dbconn('postgis', user='nobody')
    cursor = dbconn.cursor()
    stations = [station, ]
    if station.startswith("_"):
        nt = NetworkTable("RAOB")
        stations = nt.sts[station]['name'].split("--")[1].strip().split(",")

    cursor.execute("""
    SELECT f.valid at time zone 'UTC', p.levelcode, p.pressure, p.height,
    p.tmpc, p.dwpc, p.drct, round((p.smps * 1.94384)::numeric,0),
    p.bearing, p.range_miles, f.station from
    raob_profile p JOIN raob_flights f on
    (f.fid = p.fid) WHERE f.station in %s and valid >= %s and valid < %s
    """, (tuple(stations), sts, ets))
    sys.stdout.write(("station,validUTC,levelcode,pressure_mb,height_m,tmpc,"
                      "dwpc,drct,speed_kts,bearing,range_sm\n"))
    for row in cursor:
        sys.stdout.write(("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n"
                          ) % (row[10], m(row[0]),
                               m(row[1]), m(row[2]), m(row[3]), m(row[4]),
                               m(row[5]), m(row[6]), m(row[7]),
                               m(row[8]), m(row[9])))


def main():
    """Go Main Go"""
    form = cgi.FieldStorage()
    sts = datetime.datetime.strptime(form.getfirst('sts', ''),
                                     '%m/%d/%Y %H:%M')
    sts = sts.replace(tzinfo=pytz.timezone("UTC"))
    ets = datetime.datetime.strptime(form.getfirst('ets', ''),
                                     '%m/%d/%Y %H:%M')
    ets = ets.replace(tzinfo=pytz.timezone("UTC"))
    station = form.getfirst('station', 'KOAX')[:4]
    if form.getfirst('dl', None) is not None:
        sys.stdout.write('Content-type: application/octet-stream\n')
        sys.stdout.write(("Content-Disposition: attachment; "
                          "filename=%s_%s_%s.txt\n\n"
                          ) % (station, sts.strftime("%Y%m%d%H"),
                               ets.strftime("%Y%m%d%H")))
    else:
        sys.stdout.write('Content-type: text/plain\n\n')
    fetcher(station, sts, ets)


if __name__ == '__main__':
    main()
