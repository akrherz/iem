#!/usr/bin/env python
"""
Download Interface for HADS data
"""
import sys
import cgi
import datetime
import pytz
import os
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
    found = False
    res = []
    for (station, valid), row in table.iterrows():
        val = row[mycol]
        if val > threshold and not above:
            found = True
            res.append(dict(station=station, utc_valid=valid, event='START',
                            value=val))
            above = True
        if val > threshold and above:
            if val > maxrunning:
                maxrunning = val
                maxvalid = valid
        if val < threshold and above:
            res.append(dict(station=station, utc_valid=maxvalid, event='MAX',
                            value=maxrunning))
            res.append(dict(station=station, utc_valid=valid, event='END',
                            value=val))
            above = False
            maxrunning = -99
            maxvalid = None
        
    if found is False:
        error("# OOPS, did not find any exceedance!")

    return pd.DataFrame(res)

def error(msg):
    """ send back an error """
    sys.stdout.write("Content-type: text/plain\n\n")
    sys.stdout.write(msg)
    sys.exit(0)

def main():
    """ Go do something """
    form = cgi.FieldStorage()
    #network = form.getfirst('network')
    delimiter = DELIMITERS.get(form.getfirst('delim', 'comma'))
    what = form.getfirst('what', 'dl')
    threshold = float(form.getfirst('threshold', -99))
    sts, ets = get_time(form)
    stations = form.getlist('stations')
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
        table = threshold_search(table, threshold, delimiter)
    
    if what == 'txt':
        sys.stdout.write('Content-type: application/octet-stream\n')
        sys.stdout.write(('Content-Disposition: attachment; '
                          +'filename=hads.txt\n\n'))
        table.to_csv(sys.stdout, sep=delimiter)
    elif what == 'html':
        sys.stdout.write("Content-type: text/html\n\n")
        table.to_html(sys.stdout)
    elif what == 'excel':
        writer = pd.ExcelWriter('/tmp/ss.xlsx')
        table.to_excel(writer,'Data', index=True)
        writer.save()
    
        sys.stdout.write("Content-type: application/vnd.ms-excel\n")
        sys.stdout.write("Content-Disposition: attachment;Filename=hads.xlsx\n\n")
        sys.stdout.write(open('/tmp/ss.xlsx', 'rb').read())
        os.unlink('/tmp/ss.xlsx')

    else:
        sys.stdout.write("Content-type: text/plain\n\n")
        table.to_csv(sys.stdout, sep=delimiter)


if __name__ == '__main__':
    main()