#!/usr/bin/env python
"""
Download interface for TallTowers
"""

import cgi
import re
import sys
import datetime
import pytz
import psycopg2.extras
from pyiem.datatypes import temperature, speed
from pyiem import meteorology

TT = psycopg2.connect(database='talltowers',
                      host='talltowers-db.agron.iastate.edu', user='tt_web')
tcursor = TT.cursor('mystream',
                    cursor_factory=psycopg2.extras.DictCursor)


def get_stations(form):
    """ Figure out the requested station """
    if "station" not in form:
        sys.stdout.write("Content-type: text/plain \n\n")
        sys.stdout.write("ERROR: station must be specified!")
        sys.exit(0)
    stations = form.getlist("station")
    if len(stations) == 0:
        sys.stdout.write("Content-type: text/plain \n\n")
        sys.stdout.write("ERROR: station must be specified!")
        sys.exit(0)
    return stations


def get_time_bounds(form, tzinfo):
    """ Figure out the exact time bounds desired """
    y1 = int(form.getfirst('year1'))
    y2 = int(form.getfirst('year2'))
    m1 = int(form.getfirst('month1'))
    m2 = int(form.getfirst('month2'))
    d1 = int(form.getfirst('day1'))
    d2 = int(form.getfirst('day2'))
    h1 = int(form.getfirst('hour1'))
    h2 = int(form.getfirst('hour2'))
    # Construct dt instances in the right timezone, this logic sucks, but is
    # valid, have to go to UTC first then back to the local timezone
    sts = datetime.datetime.utcnow()
    sts = sts.replace(tzinfo=pytz.timezone("UTC"))
    sts = sts.astimezone(tzinfo)
    ets = sts
    try:
        sts = sts.replace(year=y1, month=m1, day=d1, hour=h1, minute=0,
                          second=0, microsecond=0)
        ets = sts.replace(year=y2, month=m2, day=d2, hour=h2, minute=0,
                          second=0, microsecond=0)
    except:
        sys.stdout.write("ERROR: Malformed Date!")
        sys.exit()

    if sts == ets:
        ets += datetime.timedelta(days=1)

    return sts, ets


def main():
    """ Go main Go """
    form = cgi.FieldStorage()
    try:
        tzinfo = pytz.timezone(form.getfirst("tz", "Etc/UTC"))
    except:
        sys.stdout.write("Invalid Timezone (tz) provided")
        sys.exit()

    # Save direct to disk or view in browser
    direct = True if form.getfirst('direct', 'no') == 'yes' else False
    stations = get_stations(form)
    if direct:
        sys.stdout.write('Content-type: application/octet-stream\n')
        fn = "%s.txt" % (stations[0],)
        if len(stations) > 1:
            fn = "asos.txt"
        sys.stdout.write('Content-Disposition: attachment; filename=%s\n\n' % (
                         fn,))
    else:
        sys.stdout.write("Content-type: text/plain \n\n")

    dbstations = stations
    if len(dbstations) == 1:
        dbstations.append('XYZXYZ')

    sts, ets = get_time_bounds(form, tzinfo)

    delim = form.getfirst("format")

    if delim == "tdf":
        rD = "\t"
    else:
        rD = ","

    sys.stdout.write("Not working yet, sorry")


if __name__ == '__main__':
    main()
