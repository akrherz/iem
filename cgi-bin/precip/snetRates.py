#!/mesonet/python/bin/python

import pg, mx.DateTime, cgi, sys
mydb = pg.connect('snet', 'iem20')

def diff(nowVal, pastVal, mulli):
  if (nowVal < 0 or pastVal < 0): return "%5s," % ("M")
  differ = nowVal - pastVal
  if differ < 0: return "%5s," % ("M")

  return "%5.2f," % (differ * mulli)

def Main():
  form = cgi.FormContent()
  year = form["year"][0]
  month = form["month"][0]
  day = form["day"][0]
  station = form["station"][0][:5]
  s = mx.DateTime.DateTime(int(year), int(month), int(day))
  e = s + mx.DateTime.RelativeDateTime(days=+1)
  interval = mx.DateTime.RelativeDateTime(minutes=+1)

  print 'Content-type: text/plain\n\n'
  print "SID  ,   DATE    ,TIME ,PCOUNT,60min ,30min ,20min ,15min ,10min , 5min , 1min ,"
  rs = mydb.query("SELECT station, valid, pday from t%s WHERE \
    station = '%s' and date(valid) = '%s' ORDER by valid ASC" \
    % (s.strftime("%Y_%m"), station, s.strftime("%Y-%m-%d") ) ).dictresult()

  pcpn = [-1]*(24*60)

  if (len(rs) == 0):
    print 'NO RESULTS FOUND FOR THIS DATE!'
    sys.exit(0)

  lminutes = 0
  lval = 0
  for i in range(len(rs)):
    ts = mx.DateTime.strptime(rs[i]['valid'][:16], "%Y-%m-%d %H:%M")
    minutes  = int((ts - s).minutes)
    val = float(rs[i]['pday'])
    pcpn[minutes] = val
    if ((val - lval) < 0.02):
      for b in range(lminutes, minutes):
        pcpn[b] = val
    lminutes = minutes
    lval = val

  for i in range(len(pcpn)):
    ts = s + (interval * i)
    print "%s,%s," % (rs[0]['station'], ts.strftime("%Y-%m-%d,%H:%M") ),
    if (pcpn[i] < 0): 
      print "%5s," % ("M"),
    else:
      print "%5.2f," % (pcpn[i],),

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
