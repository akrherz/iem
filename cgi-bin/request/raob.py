#!/usr/bin/env python
"""
Download interface for data from RAOB network
"""
import sys
import cgi
import datetime

import pytz
from pyiem.util import get_dbconn, ssw
from pyiem.network import Table as NetworkTable


def m(val):
    """Helper"""
    if val is None:
        return "M"
    return val


def fetcher(station, sts, ets):
    """Do fetching"""
    dbconn = get_dbconn("postgis")
    cursor = dbconn.cursor("raobstreamer")
    stations = [station]
    if station.startswith("_"):
        nt = NetworkTable("RAOB")
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
    ssw(
        (
            "station,validUTC,levelcode,pressure_mb,height_m,tmpc,"
            "dwpc,drct,speed_kts,bearing,range_sm\n"
        )
    )
    for row in cursor:
        ssw(
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


def friendly_date(form, key):
    """More forgiving date conversion"""
    val = form.getfirst(key)
    try:
        val = val.strip()
        if len(val.split()) == 1:
            dt = datetime.datetime.strptime(val, "%m/%d/%Y")
        else:
            dt = datetime.datetime.strptime(val, "%m/%d/%Y %H:%M")
        dt = dt.replace(tzinfo=pytz.UTC)
    except Exception:
        ssw("Content-type: text/plain\n\n")
        ssw(
            (
                'Invalid %s date provided, should be "%%m/%%d/%%Y %%H:%%M"'
                " in UTC timezone"
            )
            % (key,)
        )
        sys.exit()
    return dt


def main():
    """Go Main Go"""
    form = cgi.FieldStorage()
    sts = friendly_date(form, "sts")
    ets = friendly_date(form, "ets")

    station = form.getfirst("station", "KOAX")[:4]
    if form.getfirst("dl", None) is not None:
        ssw("Content-type: application/octet-stream\n")
        ssw(
            ("Content-Disposition: attachment; filename=%s_%s_%s.txt\n\n")
            % (station, sts.strftime("%Y%m%d%H"), ets.strftime("%Y%m%d%H"))
        )
    else:
        ssw("Content-type: text/plain\n\n")
    fetcher(station, sts, ets)


if __name__ == "__main__":
    main()
