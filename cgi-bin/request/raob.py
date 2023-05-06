"""
Download interface for data from RAOB network
"""
import datetime
from io import StringIO

import pytz
from paste.request import parse_formvars
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn


def m(val):
    """Helper"""
    if val is None:
        return "M"
    return val


def fetcher(station, sts, ets):
    """Do fetching"""
    sio = StringIO()
    dbconn = get_dbconn("raob")
    cursor = dbconn.cursor("raobstreamer")
    stations = [station]
    if station.startswith("_"):
        nt = NetworkTable("RAOB", only_online=False)
        stations = nt.sts[station]["name"].split("--")[1].strip().split(",")

    cursor.execute(
        """
    SELECT f.valid at time zone 'UTC', p.levelcode, p.pressure, p.height,
    p.tmpc, p.dwpc, p.drct, round((p.smps * 1.94384)::numeric,0),
    p.bearing, p.range_miles, f.station from
    raob_profile p JOIN raob_flights f on
    (f.fid = p.fid) WHERE f.station in %s and valid >= %s and valid < %s
    """,
        (tuple(stations), sts, ets),
    )
    sio.write(
        (
            "station,validUTC,levelcode,pressure_mb,height_m,tmpc,"
            "dwpc,drct,speed_kts,bearing,range_sm\n"
        )
    )
    for row in cursor:
        sio.write(
            ("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n")
            % (
                row[10],
                m(row[0]),
                m(row[1]),
                m(row[2]),
                m(row[3]),
                m(row[4]),
                m(row[5]),
                m(row[6]),
                m(row[7]),
                m(row[8]),
                m(row[9]),
            )
        )
    return sio.getvalue().encode("ascii", "ignore")


def friendly_date(form, key):
    """More forgiving date conversion"""
    val = form.get(key)
    try:
        val = val.strip()
        if len(val.split()) == 1:
            dt = datetime.datetime.strptime(val, "%m/%d/%Y")
        else:
            dt = datetime.datetime.strptime(val, "%m/%d/%Y %H:%M")
        dt = dt.replace(tzinfo=pytz.UTC)
    except Exception:
        return (
            f"Invalid {key} date provided, should be '%m/%d/%Y %H:%M'"
            " in UTC timezone"
        )
    return dt


def application(environ, start_response):
    """Go Main Go"""
    form = parse_formvars(environ)
    sts = friendly_date(form, "sts")
    ets = friendly_date(form, "ets")
    for val in [sts, ets]:
        if not isinstance(val, datetime.datetime):
            headers = [("Content-type", "text/plain")]
            start_response("500 Internal Server Error", headers)
            return [val.encode("ascii")]

    station = form.get("station", "KOAX")[:4]
    if form.get("dl", None) is not None:
        headers = [
            ("Content-type", "application/octet-stream"),
            (
                "Content-Disposition",
                "attachment; "
                f"filename={station}_{sts:%Y%m%d%H}_{ets:%Y%m%d%H}.txt",
            ),
        ]
    else:
        headers = [("Content-type", "text/plain")]
    start_response("200 OK", headers)
    return [fetcher(station, sts, ets)]
