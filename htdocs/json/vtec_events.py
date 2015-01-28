#!/usr/bin/env python
"""Listing of VTEC events for a WFO and year"""
import cgi
import sys
import json

def report(wfo, year):
    """Generate a report of VTEC ETNs used for a WFO and year
    
    Args:
      wfo (str): 3 character WFO identifier
      year (int): year to run for
    """
    import psycopg2
    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
    cursor = pgconn.cursor()
    
    table = "warnings_%s" % (year,)
    cursor.execute("""
    SELECT distinct phenomena, significance, eventid, 
    issue at time zone 'UTC' as utc_issue, 
    init_expire at time zone 'UTC' as utc_expire from 
    """+table+""" WHERE wfo = %s 
    ORDER by phenomena ASC, significance ASC, utc_issue ASC
    """, (wfo,))
    print '%s report for %s' % (wfo, year)
    lastrow = [None]*5
    for row in cursor:
        if row[0] != lastrow[0] or row[1] != lastrow[1]:
            print '%2s %1s %-4s %20s %20s' % ('.', '.', '.', '.', '.')
        if (row[0] == lastrow[0] and row[1] == lastrow[1] and 
            row[2] == lastrow[2] and 
            (row[3] == lastrow[3] or row[4] == lastrow[4])):
            pass
        else:
            print '%2s %1s %-4s %20s %20s' % (row[0], row[1], row[2], row[3], row[4])
        lastrow = row

def main():
    """Main()"""
    form = cgi.FieldStorage()
    wfo = form.getfirst("wfo", "MPX")
    year = int(form.getfirst("year", 2015))
    sys.stdout.write("Content-type: text/plain\n\n")
    report(wfo, year)

if __name__ == '__main__':
    main()