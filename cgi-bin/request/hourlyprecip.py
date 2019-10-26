#!/usr/bin/env python
"""Hourly precip download"""
import cgi
import datetime

import pytz
from pyiem.util import get_dbconn, ssw


def get_data(network, sts, ets, tzinfo, stations):
    """Go fetch data please"""
    pgconn = get_dbconn("iem", user="nobody")
    cursor = pgconn.cursor()
    res = "station,network,valid,precip_in\n"
    if len(stations) == 1:
        stations.append("ZZZZZ")
    cursor.execute(
        """SELECT station, network, valid, phour from
        hourly WHERE
        valid >= %s and valid < %s and network = %s and station in %s
        ORDER by valid ASC
        """,
        (sts, ets, network, tuple(stations)),
    )
    for row in cursor:
        res += ("%s,%s,%s,%s\n") % (
            row[0],
            row[1],
            (row[2].astimezone(tzinfo)).strftime("%Y-%m-%d %H:%M"),
            row[3],
        )

    return res


def main():
    """ run rabbit run """
    ssw("Content-type: text/plain\n\n")
    form = cgi.FieldStorage()
    tzinfo = pytz.timezone(form.getfirst("tz", "America/Chicago"))
    try:
        sts = datetime.date(
            int(form.getfirst("year1")),
            int(form.getfirst("month1")),
            int(form.getfirst("day1")),
        )
        ets = datetime.date(
            int(form.getfirst("year2")),
            int(form.getfirst("month2")),
            int(form.getfirst("day2")),
        )
    except Exception:
        ssw(("ERROR: Invalid date provided, please check selected dates."))
        return
    stations = form.getlist("station")
    if not stations:
        ssw(("ERROR: No stations specified for request."))
        return
    network = form.getfirst("network")[:12]
    ssw(get_data(network, sts, ets, tzinfo, stations=stations))


if __name__ == "__main__":
    # Go Main Go
    main()
