"""Hourly precip download"""
import datetime

import pytz
from paste.request import parse_formvars
from pyiem.util import get_dbconn


def get_data(network, ctx, tzinfo, stations):
    """Go fetch data please"""
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor()
    res = "station,network,valid,precip_in"
    sql = ""
    if ctx["lalo"]:
        res += ",lat,lon"
        sql += " , st_y(geom) as lat, st_x(geom) as lon "
    if ctx["st"]:
        res += ",st"
        sql += ", state "
    res += "\n"
    cursor.execute(
        f"""
        SELECT id, t.network, valid, phour {sql}
        from hourly h JOIN stations t on
        (h.iemid = t.iemid) WHERE
        valid >= %s and valid < %s and t.network = %s and t.id in %s
        ORDER by valid ASC
        """,
        (ctx["sts"], ctx["ets"], network, tuple(stations)),
    )
    for row in cursor:
        res += (
            f"{row[0]},{row[1]},{row[2].astimezone(tzinfo):%Y-%m-%d %H:%M},"
            f"{','.join([str(x) for x in row[3:]])}\n"
        )

    return res.encode("ascii", "ignore")


def application(environ, start_response):
    """run rabbit run"""
    start_response("200 OK", [("Content-type", "text/plain")])
    form = parse_formvars(environ)
    tzinfo = pytz.timezone(form.get("tz", "America/Chicago"))
    ctx = {
        "st": form.get("st") == "1",
        "lalo": form.get("lalo") == "1",
    }
    try:
        ctx["sts"] = datetime.date(
            int(form.get("year1")),
            int(form.get("month1")),
            int(form.get("day1")),
        )
        ctx["ets"] = datetime.date(
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
    return [get_data(network, ctx, tzinfo, stations=stations)]
