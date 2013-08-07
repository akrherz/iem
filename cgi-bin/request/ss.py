#!/usr/bin/env python
"""
Return a simple CSV of stuart smith data
"""

import psycopg2
import cgi
import sys
import datetime

def gage_run(sts, ets):
    """ run() """
    
    dbconn = psycopg2.connect(database='other', host='iemdb', user='nobody')
    cursor = dbconn.cursor()
    cursor.execute("""select site_serial, valid, ch1_data_p, ch2_data_p,
    ch1_data_t, ch2_data_t, ch1_data_c, ch2_data_c from ss_logger_data
    WHERE valid between %s and %s ORDER by valid ASC""", (sts, ets))
    
    res = "valid,site_serial,ch1_data_p,ch2_data_p,ch1_data_t,ch2_data_t,ch1_data_c,ch2_data_c\n"
    for row in cursor:
        res += "%s,%s,%s,%s,%s,%s,%s,%s\n" % (row[1].strftime("%Y-%m-%d %H:%M"), row[0],
                                         row[1], row[2], row[3], row[4],
                                         row[5], row[6])

    return res.replace("None", "M")

def bubbler_run(sts, ets):
    """ run() """
    
    dbconn = psycopg2.connect(database='other', host='iemdb', user='nobody')
    cursor = dbconn.cursor()
    cursor.execute("""select valid, field, value, units from ss_bubbler
    WHERE valid between %s and %s ORDER by valid ASC""", (sts, ets))
    
    res = "valid,field,value,units\n"
    for row in cursor:
        res += "%s,%s,%s,%s\n" % (row[0].strftime("%Y-%m-%d %H:%M"),
                                         row[1], row[2], row[3])

    return res.replace("None", "M")

if __name__ == '__main__':
    sys.stdout.write("Content-type: text/plain\n\n")
    form = cgi.FieldStorage()
    opt = form.getfirst('opt', 'bubbler')

    year1 = int(form.getfirst("year1"))
    year2 = int(form.getfirst("year2"))
    month1 = int(form.getfirst("month1"))
    month2 = int(form.getfirst("month2"))
    day1 = int(form.getfirst("day1"))
    day2 = int(form.getfirst("day2"))

    sts = datetime.datetime(year1, month1, day1)
    ets = datetime.datetime(year2, month2, day2)
    
    if opt == 'bubbler':
        print bubbler_run(sts, ets)
    elif opt == 'gage':
        print gage_run(sts, ets)
    
