#!/usr/bin/env python

import datetime
import cgi
import sys
import psycopg2.extras
import pytz

def diff(nowVal, pastVal, mulli):
    if nowVal < 0 or pastVal < 0:
        return "%5s," % ("M")
    differ = nowVal - pastVal
    if differ < 0:
        return "%5s," % ("M")

    return "%5.2f," % (differ * mulli)

def Main():
    form = cgi.FormContent()
    year = form["year"][0]
    month = form["month"][0]
    day = form["day"][0]
    station = form["station"][0][:5]
    s = datetime.datetime(int(year), int(month), int(day))
    s = s.replace(tzinfo=pytz.timezone("America/Chicago"))
    e = s + datetime.timedelta(days=1)
    e = e.replace(tzinfo=pytz.timezone("America/Chicago"))
    interval = datetime.timedelta(seconds=60)

    print 'Content-type: text/plain\n\n'
    print "SID  ,  DATE    ,TIME ,PCOUNT,P1MIN ,60min ,30min ,20min ,15min ,10min , 5min , 1min ,"

    if s.strftime("%Y%m%d") == datetime.datetime.now().strftime("%Y%m%d"):
        IEM = psycopg2.connect("dbname=iem host=iemdb user=nobody")
        cursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""SELECT s.id as station, valid, pday from current_log c JOIN
        stations s on (s.iemid = c.iemid) WHERE 
            s.id = %s and valid >= %s and valid < %s ORDER by valid ASC""",
             ( station, s, e ) )
    else:
        SNET = psycopg2.connect("dbname=snet host=iemdb user=nobody")
        cursor = SNET.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cursor.execute("""SELECT station, valid, pday from t"""+
                       s.strftime("%Y_%m") +""" WHERE 
            station = %s and valid >= %s and valid < %s ORDER by valid ASC""", 
            (station, s, e ) )


    pcpn = [-1]*(24*60)

    if cursor.rowcount == 0:
        print 'NO RESULTS FOUND FOR THIS DATE!'
        sys.exit(0)

    lminutes = 0
    lval = 0
    for row in cursor:
        ts = row['valid']
        minutes  = (ts - s).seconds / 60
        val = float(row['pday'])
        pcpn[minutes] = val
        if ((val - lval) < 0.02):
            for b in range(lminutes, minutes):
                pcpn[b] = val
        lminutes = minutes
        lval = val

    for i in range(len(pcpn)):
        ts = s + (interval * i)
        print "%s,%s," % (station, ts.strftime("%Y-%m-%d,%H:%M") ),
        if (pcpn[i] < 0): 
            print "%5s," % ("M"),
        else:
            print "%5.2f," % (pcpn[i],),

        if (i >= 1):
            print diff(pcpn[i], pcpn[i-1], 1),
        else:
            print "%5s," % (" "),

        if (i >= 60):
            print diff(pcpn[i], pcpn[i-60], 1),
        else:
            print "%5s," % (" "),

        if (i >= 30):
            print diff(pcpn[i], pcpn[i-30], 2),
        else:
            print "%5s," % (" "),

        if (i >= 20):
            print diff(pcpn[i], pcpn[i-20], 3),
        else:
            print "%5s," % (" "),

        if (i >= 15):
            print diff(pcpn[i], pcpn[i-15], 4),
        else:
            print "%5s," % (" "),

        if (i >= 10):
            print diff(pcpn[i], pcpn[i-10], 6),
        else:
            print "%5s," % (" "),

        if (i >= 5):
            print diff(pcpn[i], pcpn[i-5], 12),
        else:
            print "%5s," % (" "),

        if (i >= 1):
            print diff(pcpn[i], pcpn[i-1], 60),
        else:
            print "%5s," % (" "),

        print

Main()
