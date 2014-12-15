#!/usr/bin/env python
"""
Download Interface for HADS data
"""
import sys
import cgi
from pyiem.network import Table as NetworkTable
import datetime
import pytz
import pandas as pd
from pandas.io.sql import read_sql
import psycopg2
PGCONN = psycopg2.connect(database='hads', host='iemdb', user='nobody')

DELIMITERS = {'comma': ',', 'space': ' ', 'tab': '\t'}

def get_time(form):
    """ Get timestamps """
    y = int(form.getfirst('year'))
    m1 = int(form.getfirst('month1'))
    m2 = int(form.getfirst('month2'))
    d1 = int(form.getfirst('day1'))
    d2 = int(form.getfirst('day2'))
    h1 = int(form.getfirst('hour1'))
    h2 = int(form.getfirst('hour2'))
    mi1 = int(form.getfirst('minute1'))
    mi2 = int(form.getfirst('minute2'))
    sts = datetime.datetime(y, m1, d1, h1, mi1)
    sts = sts.replace(tzinfo=pytz.timezone("UTC"))
    ets = datetime.datetime(y, m2, d2, h2, mi2)
    ets = ets.replace(tzinfo=pytz.timezone("UTC"))
    return sts, ets

def threshold_search(table, threshold, delimiter):
    """ Do the threshold searching magic """
    cols = list(table.columns.values)
    searchfor = ['HGIRGZ', 'HGIRPZ', 'HGIRZZ']
    mycol = None
    for s in searchfor:
        if s in cols:
            mycol = s
            break
    if mycol is None:
        error("Could not find HG column for this site!")
        return
    above = False
    maxrunning = -99
    maxvalid = None
    sys.stdout.write("Content-type: text/plain\n\n")
    sys.stdout.write("# Threshold: %s Search Column: %s\n"% (
                            threshold, mycol))
    sys.stdout.write("STATION,UTC_VALID,EVENT,VALUE\n")
    found = False
    for (station, valid), row in table.iterrows():
        val = row[mycol]
        if val > threshold and not above:
            found = True
            sys.stdout.write("%s%s%s%s%s%s%s\n" % (station, delimiter,
                                               valid, delimiter, 'START',
                                               delimiter,val))
            above = True
        if val > threshold and above:
            if val > maxrunning:
                maxrunning = val
                maxvalid = valid
        if val < threshold and above:
            sys.stdout.write("%s%s%s%s%s%s%s\n" % (station, delimiter,
                                               maxvalid, delimiter, 'MAX',
                                               delimiter, maxrunning))
            sys.stdout.write("%s%s%s%s%s%s%s\n" % (station, delimiter,
                                               valid, delimiter, 'END',
                                               delimiter,val))
            above = False
            maxrunning = -99
            maxvalid = None
        
    if found is False:
        sys.stdout.write("# OOPS, did not find any exceedance!")

def error(msg):
    """ send back an error """
    sys.stdout.write("Content-type: text/plain\n\n")
    sys.stdout.write(msg)

def main():
    """ Go do something """
    form = cgi.FieldStorage()
    #network = form.getfirst('network')
    delimiter = DELIMITERS.get(form.getfirst('delim', 'comma'))
    what = form.getfirst('what', 'dl')
    threshold = float(form.getfirst('threshold', -99))
    sts, ets = get_time(form)
    stations = form.getlist('station')
    if len(stations) == 1:
        stations.append('XXXXXXX')
    
    table = "raw%s" % (sts.year,)
    sql = """SELECT station, valid at time zone 'UTC' as utc_valid, 
    key, value from """+table+""" 
    WHERE station in %s and valid BETWEEN '%s' and '%s'""" % (tuple(stations),
                                                              sts, ets)
    df = read_sql(sql, PGCONN)
    
    table = df.pivot_table(values='value', columns=['key'], index=['station',
                                                                   'utc_valid'])
    if threshold >= 0:
        if 'XXXXXXX' not in stations:
            error('Can not do threshold search for more than one station')
            return
        threshold_search(table, threshold, delimiter)
        return
    
    if what != 'dl':
        sys.stdout.write("Content-type: text/plain\n\n")
    else:
        sys.stdout.write('Content-type: application/octet-stream\n')
        sys.stdout.write(('Content-Disposition: attachment; '
                          +'filename=hads.txt\n\n'))

    table.to_csv(sys.stdout, sep=delimiter)

if __name__ == '__main__':
    main()