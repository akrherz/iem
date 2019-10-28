#!/usr/bin/env python
"""Queue insertion for talltowers"""

import cgi
import sys
import datetime

import pytz
from pyiem.util import get_dbconn, ssw


def send_error(msg):
    """Send an error"""
    ssw(msg)
    sys.exit(0)


def get_stations(form):
    """ Figure out the requested station """
    if "station" not in form:
        send_error("ERROR: station must be specified!")
    stations = form.getlist("station")
    if not stations:
        send_error("ERROR: station must be specified!")
    return stations


def get_time_bounds(form, tzinfo):
    """ Figure out the exact time bounds desired """
    y1 = int(form.getfirst("year1"))
    y2 = int(form.getfirst("year2"))
    m1 = int(form.getfirst("month1"))
    m2 = int(form.getfirst("month2"))
    d1 = int(form.getfirst("day1"))
    d2 = int(form.getfirst("day2"))
    h1 = int(form.getfirst("hour1"))
    h2 = int(form.getfirst("hour2"))
    # Construct dt instances in the right timezone, this logic sucks, but is
    # valid, have to go to UTC first then back to the local timezone
    sts = datetime.datetime.utcnow()
    sts = sts.replace(tzinfo=pytz.utc)
    sts = sts.astimezone(tzinfo)
    ets = sts
    try:
        sts = sts.replace(
            year=y1,
            month=m1,
            day=d1,
            hour=h1,
            minute=0,
            second=0,
            microsecond=0,
        )
        ets = sts.replace(
            year=y2,
            month=m2,
            day=d2,
            hour=h2,
            minute=0,
            second=0,
            microsecond=0,
        )
    except Exception as _:
        send_error("ERROR: Malformed Date!")

    if sts == ets:
        ets += datetime.timedelta(days=1)

    return sts, ets


def main():
    """ Go main Go """
    pgconn = get_dbconn("mesosite")
    form = cgi.FieldStorage()
    tzname = form.getfirst("tz", "Etc/UTC")
    try:
        tzinfo = pytz.timezone(tzname)
    except Exception as _:
        send_error("Invalid Timezone (tz) provided")

    stations = get_stations(form)
    sts, ets = get_time_bounds(form, tzinfo)
    fmt = form.getfirst("format")
    email = form.getfirst("email")
    aff = form.getfirst("affiliation")
    if email is None or email.find("@") == -1:
        send_error("email is required")
    if aff is None or len(aff) < 2:
        send_error("affiliation is required")

    cursor = pgconn.cursor()
    cursor.execute(
        """
    INSERT into talltowers_analog_queue
    (stations, sts, ets, fmt, email, aff) VALUES (%s, %s, %s, %s, %s, %s)
    """,
        (",".join(stations), sts, ets, fmt, email, aff),
    )
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    ssw("Content-type: text/plain\n\n")
    main()
    ssw(
        (
            "Thank you, request received, please check your "
            "email in a few minutes."
        )
    )
