"""Hourly precip download"""
import datetime

import pytz
from paste.request import parse_formvars
from pyiem.util import get_dbconn


def get_data(network, sts, ets, tzinfo, stations):
    """Go fetch data please"""
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor()
    res = "station,network,valid,precip_in\n"
    cursor.execute(
        "SELECT id, t.network, valid, phour from hourly h JOIN stations t on "
        "(h.iemid = t.iemid) WHERE "
        "valid >= %s and valid < %s and t.network = %s and t.id in %s "
        "ORDER by valid ASC",
        (sts, ets, network, tuple(stations)),
    )
    for row in cursor:
        res += (
            f"{row[0]},{row[1]},{row[2].astimezone(tzinfo):%Y-%m-%d %H:%M},"
            f"{row[3]}\n"
        )

    return res.encode("ascii", "ignore")


def application(environ, start_response):
    """run rabbit run"""
    start_response("200 OK", [("Content-type", "text/plain")])
    form = parse_formvars(environ)
    tzinfo = pytz.timezone(form.get("tz", "America/Chicago"))
    try:
        sts = datetime.date(
            int(form.get("year1")),
            int(form.get("month1")),
            int(form.get("day1")),
        )
        ets = datetime.date(
            int(form.get("year2")),
            int(form.get("month2")),
            int(form.get("day2")),
        )
    except Exception:
        return [b"ERROR: Invalid date provided, please check selected dates."]
    stations = form.getall("station")
    if not stations:
        return [b"ERROR: No stations specified for request."]
    network = form.get("network")[:12]
    return [get_data(network, sts, ets, tzinfo, stations=stations)]
