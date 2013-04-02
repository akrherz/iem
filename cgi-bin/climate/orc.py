#!/usr/bin/python
import sys
sys.path.insert(0, '/mesonet/www/apps/iemwebsite/scripts/lib')

import datetime
import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

ADJUSTMENT = 0
now = datetime.datetime.now()
e = now.replace(day=17)
s = (e - datetime.timedelta(days=31)).replace(day=17)

def averageTemp(db, hi="high", lo="low"):
    highSum, lowSum = 0, 0
    for day in db.keys():
        highSum += db[day][hi] 
        lowSum += db[day][lo] 

    highAvg = highSum / len(db)
    lowAvg = lowSum / len(db)

    return highAvg, lowAvg

def hdd(db, hi="high", lo="low"):
    dd = 0
    for day in db.keys():
        h = db[day][hi]
        l = db[day][lo] 
        a = (h+l) / 2.00
        if a < 65:
            dd += (65.0 - a)
    return dd

def cdd(db, hi="high", lo="low"):
    dd = 0
    for day in db.keys():
        h = db[day][hi]
        l = db[day][lo] 
        a = (h+l) / 2.00
        if a > 65:
            dd += (a - 65.0)
    return dd

def main():
    db = {}
    now = s
    while now <= e:
        db[ now.strftime("%m%d") ] = {'high': 'M', 'low': 'M',
                                          'avg_high': 'M', 'avg_low': 'M'}
        now += datetime.timedelta(days=1)

    # Get Sioux City data
    icursor.execute("""SELECT day, max_tmpf, min_tmpf from 
        summary s JOIN stations t ON (t.iemid = s.iemid) 
        WHERE t.id = 'SUX' and day >= '%s' and 
        day < '%s' """ % (s.strftime("%Y-%m-%d"), e.strftime("%Y-%m-%d")) )
    for row in icursor:
        db[ row[0].strftime("%m%d") ]['high'] = row[1] + ADJUSTMENT
        db[ row[0].strftime("%m%d") ]['low'] = row[2]  + ADJUSTMENT


    # Lemars
    ccursor.execute("""SELECT high, low, valid  from climate 
        WHERE station = 'IA4735'""")
    for row in ccursor:
        if not db.has_key(row[2].strftime("%m%d")):
            continue
        db[ row[2].strftime("%m%d") ]['avg_high'] = row[0] 
        db[ row[2].strftime("%m%d") ]['avg_low'] = row[1]


    # Compute Average wind speed
    acursor.execute("""
      SELECT avg(sknt) from alldata where station = 'ORC' and 
      valid BETWEEN '%s' and '%s' and sknt >= 0
      """ % (s.strftime("%Y-%m-%d %H:%M"), e.strftime("%Y-%m-%d %H:%M")))
    row = acursor.fetchone()
    awind = row[0]

    print 'Content-type: text/plain\n\n'
    print '  Orange City Climate Summary\n'
    print '%15s %6s %6s' % ("DATE", "HIGH", "LOW")
    now = s
    while now <= e:
        print "%15s %6i %6i %6i %6i" % (now.strftime("%Y-%m-%d"), 
                db[now.strftime("%m%d")]['high'], 
                db[now.strftime("%m%d")]['low'],
                db[now.strftime("%m%d")]['avg_high'], 
                db[now.strftime("%m%d")]['avg_low'])
        now += datetime.timedelta(days=1)

    h, l = averageTemp(db)
    ch, cl = averageTemp(db, "avg_high", "avg_low")

    l_hdd = hdd(db)
    c_hdd = hdd(db,"avg_high", "avg_low")

    l_cdd = cdd(db)
    c_cdd = cdd(db,"avg_high", "avg_low")

    print """
Summary Information [%s - %s]
-------------------
              Observed     |  Climate  |  Diff  
    High        %4.1f           %4.1f       %4.1f
    Low         %4.1f           %4.1f       %4.1f
 HDD(base65)    %4.0f           %4.0f       %4.0f
 CDD(base65)    %4.0f           %4.0f       %4.0f
 Wind[MPH]      %4.1f             M          M
""" % (s.strftime("%d %B %Y"), e.strftime("%d %B %Y"), h, ch, h - ch, l, cl, 
       l - cl, l_hdd, c_hdd, l_hdd - c_hdd, l_cdd, c_cdd, l_cdd - c_cdd,
       awind)


main()
