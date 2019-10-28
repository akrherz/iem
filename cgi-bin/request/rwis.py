#!/usr/bin/env python
"""Download Interface for RWIS data"""
import sys
import cgi
import datetime
import os
from io import StringIO

import pytz
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, ssw

PGCONN = get_dbconn("rwis")

DELIMITERS = {"comma": ",", "space": " ", "tab": "\t"}


def get_time(form, tzname):
    """ Get timestamps """
    ts = datetime.datetime.utcnow()
    ts = ts.replace(tzinfo=pytz.utc)
    ts = ts.astimezone(pytz.timezone(tzname))
    y1 = int(form.getfirst("year1"))
    y2 = int(form.getfirst("year2"))
    m1 = int(form.getfirst("month1"))
    m2 = int(form.getfirst("month2"))
    d1 = int(form.getfirst("day1"))
    d2 = int(form.getfirst("day2"))
    h1 = int(form.getfirst("hour1"))
    h2 = int(form.getfirst("hour2"))
    mi1 = int(form.getfirst("minute1", 0))
    mi2 = int(form.getfirst("minute2", 0))
    sts = ts.replace(year=y1, month=m1, day=d1, hour=h1, minute=mi1)
    ets = ts.replace(year=y2, month=m2, day=d2, hour=h2, minute=mi2)
    return sts, ets


def error(msg):
    """ send back an error """
    ssw("Content-type: text/plain\n\n")
    ssw(msg)
    sys.exit(0)


def main():
    """ Go do something """
    form = cgi.FieldStorage()
    include_latlon = form.getfirst("gis", "no").lower() == "yes"
    myvars = form.getlist("vars")
    myvars.insert(0, "station")
    myvars.insert(1, "obtime")
    delimiter = DELIMITERS.get(form.getfirst("delim", "comma"))
    what = form.getfirst("what", "dl")
    tzname = form.getfirst("tz", "UTC")
    src = form.getfirst("src", "atmos")
    sts, ets = get_time(form, tzname)
    stations = form.getlist("stations")
    if not stations:
        ssw("Content-type: text/plain\n\n")
        ssw("Error, no stations specified for the query!")
        return
    if len(stations) == 1:
        stations.append("XXXXXXX")

    tbl = ""
    if src in ["soil", "traffic"]:
        tbl = "_%s" % (src,)
    sql = (
        """SELECT *, valid at time zone %s as obtime from
    alldata"""
        + tbl
        + """
    WHERE station in %s and valid BETWEEN %s and %s ORDER by valid ASC
    """
    )
    df = read_sql(sql, PGCONN, params=(tzname, tuple(stations), sts, ets))
    if df.empty:
        ssw("Content-type: text/plain\n\n")
        ssw("Sorry, no results found for query!")
        return
    if include_latlon:
        network = form.getfirst("network")
        nt = NetworkTable(network)
        myvars.insert(2, "longitude")
        myvars.insert(3, "latitude")

        def get_lat(station):
            """hack"""
            return nt.sts[station]["lat"]

        def get_lon(station):
            """hack"""
            return nt.sts[station]["lon"]

        df["latitude"] = [get_lat(x) for x in df["station"]]
        df["longitude"] = [get_lon(x) for x in df["station"]]

    sio = StringIO()
    if what == "txt":
        ssw("Content-type: application/octet-stream\n")
        ssw(("Content-Disposition: attachment; filename=rwis.txt\n\n"))
        df.to_csv(sio, index=False, sep=delimiter, columns=myvars)
    elif what == "html":
        ssw("Content-type: text/html\n\n")
        df.to_html(sio, columns=myvars)
    elif what == "excel":
        writer = pd.ExcelWriter("/tmp/ss.xlsx")
        df.to_excel(writer, "Data", index=False, columns=myvars)
        writer.save()

        ssw("Content-type: application/vnd.ms-excel\n")
        ssw(("Content-Disposition: attachment; Filename=rwis.xlsx\n\n"))
        ssw(open("/tmp/ss.xlsx", "rb").read())
        os.unlink("/tmp/ss.xlsx")
        return
    else:
        ssw("Content-type: text/plain\n\n")
        df.to_csv(sio, sep=delimiter, columns=myvars)
    sio.seek(0)
    ssw(sio.getvalue())


if __name__ == "__main__":
    main()
