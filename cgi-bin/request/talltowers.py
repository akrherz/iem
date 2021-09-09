"""Queue insertion for talltowers"""
import datetime

import pytz
from paste.request import parse_formvars
from pyiem.util import get_dbconn


def get_stations(form):
    """Figure out the requested station"""
    stations = form.getall("station")
    return stations


def get_time_bounds(form, tzinfo):
    """Figure out the exact time bounds desired"""
    y1 = int(form.get("year1"))
    y2 = int(form.get("year2"))
    m1 = int(form.get("month1"))
    m2 = int(form.get("month2"))
    d1 = int(form.get("day1"))
    d2 = int(form.get("day2"))
    h1 = int(form.get("hour1"))
    h2 = int(form.get("hour2"))
    # Construct dt instances in the right timezone, this logic sucks, but is
    # valid, have to go to UTC first then back to the local timezone
    sts = datetime.datetime.utcnow()
    sts = sts.replace(tzinfo=pytz.UTC)
    sts = sts.astimezone(tzinfo)

    sts = sts.replace(
        year=y1, month=m1, day=d1, hour=h1, minute=0, second=0, microsecond=0
    )
    ets = sts.replace(
        year=y2, month=m2, day=d2, hour=h2, minute=0, second=0, microsecond=0
    )

    if sts == ets:
        ets += datetime.timedelta(days=1)

    return sts, ets


def application(environ, start_response):
    """Go main Go"""
    pgconn = get_dbconn("mesosite")
    form = parse_formvars(environ)
    tzname = form.get("tz", "Etc/UTC")
    start_response("200 OK", [("Content-type", "text/plain")])
    try:
        tzinfo = pytz.timezone(tzname)
    except Exception:
        return [b"Invalid Timezone (tz) provided"]

    stations = get_stations(form)
    if not stations:
        return [b"No stations provided"]
    sts, ets = get_time_bounds(form, tzinfo)
    fmt = form.get("format")
    email = form.get("email")
    aff = form.get("affiliation")
    if email is None or email.find("@") == -1:
        return [b"email is required"]
    if aff is None or len(aff) < 2:
        return [b"affiliation is required"]

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
    return [b"Submitted, thank you!"]
