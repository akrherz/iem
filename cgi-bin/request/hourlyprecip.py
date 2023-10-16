"""Hourly precip download"""
import datetime
from zoneinfo import ZoneInfo

from pyiem.util import get_dbconn
from pyiem.webutil import iemapp


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
        valid >= %s and valid < %s and t.network = %s and t.id = ANY(%s)
        ORDER by valid ASC
        """,
        (ctx["sts"], ctx["ets"], network, stations),
    )
    for row in cursor:
        res += (
            f"{row[0]},{row[1]},{row[2].astimezone(tzinfo):%Y-%m-%d %H:%M},"
            f"{','.join([str(x) for x in row[3:]])}\n"
        )

    return res.encode("ascii", "ignore")


@iemapp()
def application(environ, start_response):
    """run rabbit run"""
    start_response("200 OK", [("Content-type", "text/plain")])
    tzinfo = ZoneInfo(environ.get("tz", "America/Chicago"))
    ctx = {
        "st": environ.get("st") == "1",
        "lalo": environ.get("lalo") == "1",
    }
    try:
        ctx["sts"] = datetime.date(
            int(environ.get("year1")),
            int(environ.get("month1")),
            int(environ.get("day1")),
        )
        ctx["ets"] = datetime.date(
            int(environ.get("year2")),
            int(environ.get("month2")),
            int(environ.get("day2")),
        )
    except Exception:
        return [b"ERROR: Invalid date provided, please check selected dates."]
    stations = environ.get("station", [])
    if isinstance(stations, str):
        stations = [stations]
    if not stations:
        return [b"ERROR: No stations specified for request."]
    network = environ.get("network")[:12]
    return [get_data(network, ctx, tzinfo, stations=stations)]
