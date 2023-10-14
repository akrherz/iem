"""Legacy stuff."""
import datetime
from io import StringIO
from zoneinfo import ZoneInfo

from pyiem.util import get_dbconnc
from pyiem.webutil import iemapp


def diff(nowVal, pastVal, mulli):
    """t"""
    if nowVal < 0 or pastVal < 0:
        return "%5s," % ("M")
    differ = nowVal - pastVal
    if differ < 0:
        return "%5s," % ("M")

    return "%5.2f," % (differ * mulli)


@iemapp()
def application(environ, start_response):
    """Go Main."""
    sio = StringIO()
    start_response("200 OK", [("Content-type", "text/plain")])
    year = environ.get("year", 2010)
    month = environ.get("month", 6)
    day = environ.get("day", 7)
    station = environ.get("station", "SAMI4")[:5]
    s = datetime.datetime(int(year), int(month), int(day))
    s = s.replace(tzinfo=ZoneInfo("America/Chicago"))
    e = s + datetime.timedelta(days=1)
    e = e.replace(tzinfo=ZoneInfo("America/Chicago"))
    interval = datetime.timedelta(seconds=60)

    sio.write(
        "SID  ,  DATE    ,TIME ,PCOUNT,P1MIN ,60min ,30min ,20min "
        ",15min ,10min , 5min , 1min ,"
    )

    if s.strftime("%Y%m%d") == datetime.datetime.now().strftime("%Y%m%d"):
        IEM, cursor = get_dbconnc("iem")
        cursor.execute(
            """SELECT s.id as station, valid, pday from current_log c JOIN
        stations s on (s.iemid = c.iemid) WHERE
            s.id = %s and valid >= %s and valid < %s ORDER by valid ASC""",
            (station, s, e),
        )
    else:
        SNET, cursor = get_dbconnc("snet")

        cursor.execute(
            """SELECT station, valid, pday from t"""
            + s.strftime("%Y_%m")
            + """ WHERE
            station = %s and valid >= %s and valid < %s ORDER by valid ASC""",
            (station, s, e),
        )

    pcpn = [-1] * (24 * 60)

    if cursor.rowcount == 0:
        return [b"NO RESULTS FOUND FOR THIS DATE!"]

    lminutes = 0
    lval = 0
    for row in cursor:
        ts = row["valid"]
        minutes = (ts - s).seconds // 60
        val = float(row["pday"])
        pcpn[minutes] = val
        if (val - lval) < 0.02:
            for b in range(lminutes, minutes):
                pcpn[b] = val
        lminutes = minutes
        lval = val

    for i, val in enumerate(pcpn):
        ts = s + (interval * i)
        sio.write("%s,%s," % (station, ts.strftime("%Y-%m-%d,%H:%M")))
        if pcpn[i] < 0:
            sio.write("%5s," % ("M"))
        else:
            sio.write("%5.2f," % (val,))

        if i >= 1:
            sio.write(diff(pcpn[i], pcpn[i - 1], 1))
        else:
            sio.write("%5s," % (" "))

        if i >= 60:
            sio.write(diff(pcpn[i], pcpn[i - 60], 1))
        else:
            sio.write("%5s," % (" "))

        if i >= 30:
            sio.write(diff(pcpn[i], pcpn[i - 30], 2))
        else:
            sio.write("%5s," % (" "))

        if i >= 20:
            sio.write(diff(pcpn[i], pcpn[i - 20], 3))
        else:
            sio.write("%5s," % (" "))

        if i >= 15:
            sio.write(diff(pcpn[i], pcpn[i - 15], 4))
        else:
            sio.write("%5s," % (" "))

        if i >= 10:
            sio.write(diff(pcpn[i], pcpn[i - 10], 6))
        else:
            sio.write("%5s," % (" "))

        if i >= 5:
            sio.write(diff(pcpn[i], pcpn[i - 5], 12))
        else:
            sio.write("%5s," % (" "))

        if i >= 1:
            sio.write(diff(pcpn[i], pcpn[i - 1], 60))
        else:
            sio.write("%5s," % (" "))

        sio.write("\n")
    return [sio.getvalue().encode("ascii")]
