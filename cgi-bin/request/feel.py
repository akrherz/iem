#!/usr/bin/env python

import pandas as pd
import sys
import cgi
import datetime
import psycopg2
import os


def run(sts, ets):
    """ Get data! """
    dbconn = psycopg2.connect(database='other', host='iemdb', user='nobody')
    sql = """SELECT * from feel_data_daily where
    valid >= '%s' and valid < '%s' ORDER by valid ASC""" % (sts, ets)
    df = pd.read_sql(sql, dbconn)

    sql = """SELECT * from feel_data_hourly where
    valid >= '%s' and valid < '%s' ORDER by valid ASC""" % (sts, ets)
    df2 = pd.read_sql(sql, dbconn)

    writer = pd.ExcelWriter('/tmp/ss.xlsx')
    df.to_excel(writer, 'Daily Data', index=False)
    df2.to_excel(writer, 'Hourly Data', index=False)
    writer.save()

    sys.stdout.write("Content-type: application/vnd.ms-excel\n")
    sys.stdout.write("Content-Disposition: attachment;Filename=feel.xls\n\n")
    sys.stdout.write(open('/tmp/ss.xlsx', 'rb').read())
    os.unlink('/tmp/ss.xlsx')


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

if __name__ == '__main__':
    main()
