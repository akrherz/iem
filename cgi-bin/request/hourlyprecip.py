"""Hourly precip download"""

from zoneinfo import ZoneInfo

from pyiem.exceptions import IncompleteWebRequest
from pyiem.util import get_dbconn
from pyiem.webutil import ensure_list, iemapp


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
    tzinfo = ZoneInfo(environ.get("tz", "America/Chicago"))
    if "sts" not in environ:
        raise IncompleteWebRequest("No year1,month1,day1 was specified.")
    ctx = {
        "st": environ.get("st") == "1",
        "lalo": environ.get("lalo") == "1",
        "sts": environ["sts"].date(),
        "ets": environ["ets"].date(),
    }
    stations = ensure_list(environ, "station")
    if not stations:
        raise IncompleteWebRequest("No station= was specified.")
    start_response("200 OK", [("Content-type", "text/plain")])
    network = environ.get("network")[:12]
    return [get_data(network, ctx, tzinfo, stations=stations)]
