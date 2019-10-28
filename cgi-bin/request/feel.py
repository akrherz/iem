#!/usr/bin/env python
"""FEEL data download"""
# pylint: disable=abstract-class-instantiated
import cgi
import datetime
import os

import pandas as pd
from pyiem.util import get_dbconn, ssw


def run(sts, ets):
    """ Get data! """
    dbconn = get_dbconn("other", user="nobody")
    sql = """SELECT * from feel_data_daily where
    valid >= '%s' and valid < '%s' ORDER by valid ASC""" % (
        sts,
        ets,
    )
    df = pd.read_sql(sql, dbconn)

    sql = """SELECT * from feel_data_hourly where
    valid >= '%s' and valid < '%s' ORDER by valid ASC""" % (
        sts,
        ets,
    )
    df2 = pd.read_sql(sql, dbconn)

    def fmt(val):
        """Lovely hack."""
        return val.strftime("%Y-%m-%d %H:%M")

    df2["valid"] = df2["valid"].apply(fmt)

    with pd.ExcelWriter("/tmp/ss.xlsx") as writer:
        df.to_excel(writer, "Daily Data", index=False)
        df2.to_excel(writer, "Hourly Data", index=False)

    ssw("Content-type: application/vnd.ms-excel\n")
    ssw("Content-Disposition: attachment;Filename=feel.xls\n\n")
    ssw(open("/tmp/ss.xlsx", "rb").read())
    os.unlink("/tmp/ss.xlsx")


def main():
    """ Get stuff """
    form = cgi.FieldStorage()
    year1 = int(form.getfirst("year1"))
    year2 = int(form.getfirst("year2"))
    month1 = int(form.getfirst("month1"))
    month2 = int(form.getfirst("month2"))
    day1 = int(form.getfirst("day1"))
    day2 = int(form.getfirst("day2"))

    sts = datetime.datetime(year1, month1, day1)
    ets = datetime.datetime(year2, month2, day2)

    run(sts, ets)


if __name__ == "__main__":
    main()
