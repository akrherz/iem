#!/usr/bin/env python
"""
Download Interface for HADS data
"""
import sys
import cgi
import os
from io import StringIO

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn, utc, ssw

PGCONN = get_dbconn("hads")
DELIMITERS = {"comma": ",", "space": " ", "tab": "\t"}


def get_time(form):
    """ Get timestamps """
    y1 = int(form.getfirst("year"))
    m1 = int(form.getfirst("month1"))
    m2 = int(form.getfirst("month2"))
    d1 = int(form.getfirst("day1"))
    d2 = int(form.getfirst("day2"))
    h1 = int(form.getfirst("hour1"))
    h2 = int(form.getfirst("hour2"))
    mi1 = int(form.getfirst("minute1"))
    mi2 = int(form.getfirst("minute2"))
    sts = utc(y1, m1, d1, h1, mi1)
    ets = utc(y1, m2, d2, h2, mi2)
    return sts, ets


def threshold_search(table, threshold, thresholdvar, delimiter):
    """ Do the threshold searching magic """
    cols = list(table.columns.values)
    searchfor = "HGI%s" % (thresholdvar.upper(),)
    cols5 = [s[:5] for s in cols]
    if searchfor not in cols5:
        error("Could not find %s variable for this site!" % (searchfor,))
        return
    mycol = cols[cols5.index(searchfor)]
    above = False
    maxrunning = -99
    maxvalid = None
    found = False
    res = []
    for (station, valid), row in table.iterrows():
        val = row[mycol]
        if val > threshold and not above:
            found = True
            res.append(
                dict(
                    station=station,
                    utc_valid=valid,
                    event="START",
                    value=val,
                    varname=mycol,
                )
            )
            above = True
        if val > threshold and above:
            if val > maxrunning:
                maxrunning = val
                maxvalid = valid
        if val < threshold and above:
            res.append(
                dict(
                    station=station,
                    utc_valid=maxvalid,
                    event="MAX",
                    value=maxrunning,
                    varname=mycol,
                )
            )
            res.append(
                dict(
                    station=station,
                    utc_valid=valid,
                    event="END",
                    value=val,
                    varname=mycol,
                )
            )
            above = False
            maxrunning = -99
            maxvalid = None

    if found is False:
        error("# OOPS, did not find any exceedance!")

    return pd.DataFrame(res)


def error(msg):
    """ send back an error """
    ssw("Content-type: text/plain\n\n")
    ssw(msg)
    sys.exit(0)


def main():
    """ Go do something """
    form = cgi.FieldStorage()
    # network = form.getfirst('network')
    delimiter = DELIMITERS.get(form.getfirst("delim", "comma"))
    what = form.getfirst("what", "dl")
    threshold = float(form.getfirst("threshold", -99))
    thresholdvar = form.getfirst("threshold-var", "RG")
    sts, ets = get_time(form)
    stations = form.getlist("stations")
    if not stations:
        ssw("Content-type: text/plain\n\n")
        ssw("Error, no stations specified for the query!")
        return
    if len(stations) == 1:
        stations.append("XXXXXXX")

    table = "raw%s" % (sts.year,)
    sql = (
        """SELECT station, valid at time zone 'UTC' as utc_valid,
    key, value from """
        + table
        + """
    WHERE station in %s and valid BETWEEN '%s' and '%s'
    and value > -999"""
        % (tuple(stations), sts, ets)
    )
    df = read_sql(sql, PGCONN)
    if df.empty:
        ssw("Content-type: text/plain\n\n")
        ssw("Sorry, no results found for query!")
        return
    table = df.pivot_table(
        values="value", columns=["key"], index=["station", "utc_valid"]
    )
    if threshold >= 0:
        if "XXXXXXX" not in stations:
            error("Can not do threshold search for more than one station")
            return
        table = threshold_search(table, threshold, thresholdvar, delimiter)

    bio = StringIO()
    if what == "txt":
        ssw("Content-type: application/octet-stream\n")
        ssw(("Content-Disposition: attachment; filename=hads.txt\n\n"))
        table.to_csv(bio, sep=delimiter)
    elif what == "html":
        ssw("Content-type: text/html\n\n")
        table.to_html(bio)
    elif what == "excel":
        writer = pd.ExcelWriter("/tmp/ss.xlsx")
        table.to_excel(writer, "Data", index=True)
        writer.save()

        ssw("Content-type: application/vnd.ms-excel\n")
        ssw(("Content-Disposition: attachment; Filename=hads.xlsx\n\n"))
        ssw(open("/tmp/ss.xlsx", "rb").read())
        os.unlink("/tmp/ss.xlsx")
        return
    else:
        ssw("Content-type: text/plain\n\n")
        table.to_csv(bio, sep=delimiter)
    bio.seek(0)
    ssw(bio.getvalue())


if __name__ == "__main__":
    main()
