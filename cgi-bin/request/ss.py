#!/usr/bin/env python
"""
Return a simple CSV of stuart smith data

Levelogger Reading (ft)
Barologger Reading
Temp (C)
Barologger Air Temp (C)
Conductivity (micro-S)
7.20473    ch1_data_p
2.68857     ch2_data_p
21.1       ch1_data_t
18.19    ch2_data_t
48       ch1_data_c
"""
import cgi
import datetime
import os

import pandas as pd
from pyiem.util import get_dbconn, ssw

LOOKUP = {
    9100104: "SSP #6",
    9100135: "SSP #8",
    9100131: "SSP #1",
    9100156: "SSP #7",
}


def gage_run(sts, ets, stations, excel):
    """ run() """
    if not stations:
        stations = LOOKUP.keys()
    if len(stations) == 1:
        stations.append(0)

    dbconn = get_dbconn("other", user="nobody")
    sql = """select date(valid) as date, to_char(valid, 'HH24:MI:SS') as time,
    site_serial, ch1_data_p, ch2_data_p,
    ch1_data_t, ch2_data_t, ch1_data_c
    from ss_logger_data WHERE valid between '%s' and '%s' and
    site_serial in %s ORDER by valid ASC""" % (
        sts,
        ets,
        str(tuple(stations)),
    )
    df = pd.read_sql(sql, dbconn)
    headers = [
        "date",
        "time",
        "site_serial",
        "Levelogger Reading (ft)",
        "Barologger Reading",
        "Water Temp (C)",
        "Barologger Air Temp (C)",
        "Conductivity (micro-S)",
    ]

    if excel == "yes":
        ssw("Content-type: application/vnd.ms-excel\n")
        ssw(("Content-Disposition: attachment; Filename=stuartsmith.xls\n\n"))
        df.to_excel("/tmp/ss.xls", header=headers, index=False)
        ssw(open("/tmp/ss.xls", "rb").read())
        os.unlink("/tmp/ss.xls")
    else:
        ssw("Content-type: text/plain\n\n")
        ssw(df.to_csv(None, header=headers, index=False))


def bubbler_run(sts, ets, excel):
    """ run() """
    dbconn = get_dbconn("other", user="nobody")
    sql = """
    WITH one as (SELECT valid, value from ss_bubbler WHERE
    valid between '%s' and '%s' and field = 'Batt Voltage'),
    two as (SELECT valid, value from ss_bubbler WHERE
    valid between '%s' and '%s' and field = 'STAGE'),
    three as (SELECT valid, value from ss_bubbler WHERE
    valid between '%s' and '%s' and field = 'Water Temp')

    SELECT date(coalesce(one.valid, two.valid, three.valid)) as date,
    to_char(coalesce(one.valid, two.valid, three.valid), 'HH24:MI:SS') as time,
    one.value, two.value, three.value
    from one FULL OUTER JOIN two on (one.valid = two.valid)
        FULL OUTER JOIN three on (coalesce(two.valid,one.valid) = three.valid)
    ORDER by date ASC, time ASC
    """ % (
        sts,
        ets,
        sts,
        ets,
        sts,
        ets,
    )
    df = pd.read_sql(sql, dbconn)
    headers = ["date", "time", "batt voltage", "stage", "water temp"]

    if excel == "yes":
        ssw("Content-type: application/vnd.ms-excel\n")
        ssw(("Content-Disposition: attachment; Filename=bubbler.xls\n\n"))
        df.to_excel("/tmp/ss.xls", header=headers, index=False)
        ssw(open("/tmp/ss.xls", "rb").read())
        os.unlink("/tmp/ss.xls")
    else:
        ssw("Content-type: text/plain\n\n")
        ssw(df.to_csv(None, header=headers, index=False))


def main():
    """ Go Main Go """
    form = cgi.FieldStorage()
    opt = form.getfirst("opt", "bubbler")

    year1 = int(form.getfirst("year1"))
    year2 = int(form.getfirst("year2"))
    month1 = int(form.getfirst("month1"))
    month2 = int(form.getfirst("month2"))
    day1 = int(form.getfirst("day1"))
    day2 = int(form.getfirst("day2"))
    stations = form.getlist("station")

    sts = datetime.datetime(year1, month1, day1)
    ets = datetime.datetime(year2, month2, day2)

    if opt == "bubbler":
        bubbler_run(sts, ets, form.getfirst("excel", "n"))
    elif opt == "gage":
        gage_run(sts, ets, stations, form.getfirst("excel", "n"))


if __name__ == "__main__":
    main()
