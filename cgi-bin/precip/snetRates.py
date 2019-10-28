#!/usr/bin/env python
import datetime
import cgi
import sys

import psycopg2.extras
import pytz
from pyiem.util import get_dbconn, ssw


def diff(nowVal, pastVal, mulli):
    if nowVal < 0 or pastVal < 0:
        return "%5s," % ("M")
    differ = nowVal - pastVal
    if differ < 0:
        return "%5s," % ("M")

    return "%5.2f," % (differ * mulli)


def main():
    form = cgi.FieldStorage()
    year = form.getfirst("year")
    month = form.getfirst("month")
    day = form.getfirst("day")
    station = form.getfirst("station", "SAMI4")[:5]
    s = datetime.datetime(int(year), int(month), int(day))
    s = s.replace(tzinfo=pytz.timezone("America/Chicago"))
    e = s + datetime.timedelta(days=1)
    e = e.replace(tzinfo=pytz.timezone("America/Chicago"))
    interval = datetime.timedelta(seconds=60)

    ssw("Content-type: text/plain\n\n")
    ssw(
        "SID  ,  DATE    ,TIME ,PCOUNT,P1MIN ,60min ,30min ,20min ,15min ,10min , 5min , 1min ,"
    )

    if s.strftime("%Y%m%d") == datetime.datetime.now().strftime("%Y%m%d"):
        IEM = get_dbconn("iem")
        cursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute(
            """SELECT s.id as station, valid, pday from current_log c JOIN
        stations s on (s.iemid = c.iemid) WHERE
            s.id = %s and valid >= %s and valid < %s ORDER by valid ASC""",
            (station, s, e),
        )
    else:
        SNET = get_dbconn("snet")
        cursor = SNET.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cursor.execute(
            """SELECT station, valid, pday from t"""
            + s.strftime("%Y_%m")
            + """ WHERE 
            station = %s and valid >= %s and valid < %s ORDER by valid ASC""",
            (station, s, e),
        )

    pcpn = [-1] * (24 * 60)

    if cursor.rowcount == 0:
        ssw("NO RESULTS FOUND FOR THIS DATE!")
        sys.exit(0)

    lminutes = 0
    lval = 0
    for row in cursor:
        ts = row["valid"]
        minutes = (ts - s).seconds / 60
        val = float(row["pday"])
        pcpn[minutes] = val
        if (val - lval) < 0.02:
            for b in range(lminutes, minutes):
                pcpn[b] = val
        lminutes = minutes
        lval = val

    for i in range(len(pcpn)):
        ts = s + (interval * i)
        ssw("%s,%s," % (station, ts.strftime("%Y-%m-%d,%H:%M")))
        if pcpn[i] < 0:
            ssw("%5s," % ("M"))
        else:
            ssw("%5.2f," % (pcpn[i],))

        if i >= 1:
            ssw(diff(pcpn[i], pcpn[i - 1], 1))
        else:
            ssw("%5s," % (" "))

        if i >= 60:
            ssw(diff(pcpn[i], pcpn[i - 60], 1))
        else:
            ssw("%5s," % (" "))

        if i >= 30:
            ssw(diff(pcpn[i], pcpn[i - 30], 2))
        else:
            ssw("%5s," % (" "))

        if i >= 20:
            ssw(diff(pcpn[i], pcpn[i - 20], 3))
        else:
            ssw("%5s," % (" "))

        if i >= 15:
            ssw(diff(pcpn[i], pcpn[i - 15], 4))
        else:
            ssw("%5s," % (" "))

        if i >= 10:
            ssw(diff(pcpn[i], pcpn[i - 10], 6))
        else:
            ssw("%5s," % (" "))

        if i >= 5:
            ssw(diff(pcpn[i], pcpn[i - 5], 12))
        else:
            ssw("%5s," % (" "))

        if i >= 1:
            ssw(diff(pcpn[i], pcpn[i - 1], 60))
        else:
            ssw("%5s," % (" "))

        ssw("\n")


if __name__ == "__main__":
    main()
