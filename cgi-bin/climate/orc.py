#!/mesonet/python/bin/python

import mx.DateTime
from pyIEM import iemAccess, iemdb
#iemaccess = iemAccess.iemAccess()
#i = iemdb.iemdb()
#climatedb = i["coop"]
import pg
climatedb = pg.connect('coop','iemdb', user='nobody')
iemaccess = pg.connect('iem', 'iemdb', user='nobody')

ADJUSTMENT = 0
s = mx.DateTime.DateTime(2008,3,18)
e = mx.DateTime.DateTime(2008,4,17)
interval = mx.DateTime.RelativeDateTime(days=+1)

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
    if (a < 65):
      dd += (65.0 - a)
  return dd

def cdd(db, hi="high", lo="low"):
  dd = 0
  for day in db.keys():
    h = db[day][hi]
    l = db[day][lo] 
    a = (h+l) / 2.00
    if (a > 65):
      dd += (a - 65.0)
  return dd

def main():
  db = {}
  now = s
  while (now <= e):
    db[ now.strftime("%Y-%m-%d") ] = {'high': 'M', 'low': 'M',
        'avg_high': 'M', 'avg_low': 'M'}
    now += interval

  rs = iemaccess.query("SELECT day, max_tmpf, min_tmpf from summary_%s \
    WHERE station = 'SUX'" % (now.year -1, ) ).dictresult()

  for i in range(len(rs)):
    if (db.has_key( rs[i]['day'] )):
      db[ rs[i]['day'] ]['high'] = rs[i]['max_tmpf'] + ADJUSTMENT
      db[ rs[i]['day'] ]['low'] = rs[i]['min_tmpf']  + ADJUSTMENT

  rs = iemaccess.query("SELECT day, max_tmpf, min_tmpf from summary_%s \
    WHERE station = 'SUX'" % (now.year, ) ).dictresult()

  for i in range(len(rs)):
    if (db.has_key( rs[i]['day'] )):
      db[ rs[i]['day'] ]['high'] = rs[i]['max_tmpf'] + ADJUSTMENT
      db[ rs[i]['day'] ]['low'] = rs[i]['min_tmpf']  + ADJUSTMENT

  # Lemars
  rs = climatedb.query("SELECT high, low, \
    to_char(valid, '2008-mm-dd') as valid from climate \
    WHERE station = 'ia4735'").dictresult()

  for i in range(len(rs)):
    if (db.has_key( rs[i]['valid'] )):
      db[ rs[i]['valid'] ]['avg_high'] = rs[i]['high'] 
      db[ rs[i]['valid'] ]['avg_low'] = rs[i]['low']

  rs = climatedb.query("SELECT high, low, \
    to_char(valid, '2009-mm-dd') as valid from climate \
    WHERE station = 'ia4735'").dictresult()
                                                                                
  for i in range(len(rs)):
    if (db.has_key( rs[i]['valid'] )):
      db[ rs[i]['valid'] ]['avg_high'] = rs[i]['high']
      db[ rs[i]['valid'] ]['avg_low'] = rs[i]['low']


  print 'Content-type: text/plain\n\n'
  print '  Orange City Climate Summary\n'
  print '%15s %6s %6s' % ("DATE", "HIGH", "LOW")
  now = s
  while (now <= e):
    print "%15s %6i %6i %6i %6i" % (now.strftime("%Y-%m-%d"), \
     db[now.strftime("%Y-%m-%d")]['high'], db[now.strftime("%Y-%m-%d")]['low'],\
     db[now.strftime("%Y-%m-%d")]['avg_high'], db[now.strftime("%Y-%m-%d")]['avg_low'])
    now += interval

  h, l = averageTemp(db)
  ch, cl = averageTemp(db, "avg_high", "avg_low")

  l_hdd = hdd(db)
  c_hdd = hdd(db,"avg_high", "avg_low")

  l_cdd = cdd(db)
  c_cdd = cdd(db,"avg_high", "avg_low")

  print """
Summary Information
-------------------
              Observed     |  Climate  |  Diff  
    High        %4.1f           %4.1f       %4.1f
    Low         %4.1f           %4.1f       %4.1f
 HDD(base65)    %4.0f           %4.0f       %4.0f
 CDD(base65)    %4.0f           %4.0f       %4.0f
""" % (h, ch, h - ch, l, cl, l - cl, l_hdd, c_hdd, l_hdd - c_hdd, l_cdd, c_cdd, l_cdd - c_cdd)


main()
