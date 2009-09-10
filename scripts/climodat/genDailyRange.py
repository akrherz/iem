#!/mesonet/python/bin/python
# Daryl Herzmann 3 Mar 2004

_REPORTID = "06"

def go(mydb, rs, stationID):
  import mx.DateTime, constants
  s = mx.DateTime.DateTime(2000, 1, 1)
  e = mx.DateTime.DateTime(2001, 1, 1)
  interval = mx.DateTime.RelativeDateTime(days=+1)
  r = {}
  now = s
  while (now < e):
   r[now] = {'max': 0, 'min': 100}
   now += interval

  for i in range(len(rs)):
    valid = mx.DateTime.strptime(rs[i]["day"], "%Y-%m-%d")
    valid += mx.DateTime.RelativeDateTime(year=2000)
    try:
      high = int(rs[i]["high"])
      low = int(rs[i]["low"])
      tr = high - low
    except:
      continue
    if (tr > r[valid]["max"]):
      r[valid]["max"] = tr
    if (tr < r[valid]["min"]):
      r[valid]["min"] = tr

  for day in r.keys():
    sql = "UPDATE %s SET max_range = %s, min_range = %s \
      WHERE station = '%s' and valid = '%s' " % (constants.climatetable(stationID), r[day]["max"], \
      r[day]["min"], stationID, day.strftime("%Y-%m-%d") )
    mydb.query(sql)

def write(mydb, stationID):
  import mx.DateTime, constants
  r = {}
  out = open("reports/%s_%s.txt" % (stationID, _REPORTID), 'w')
  constants.writeheader(out, stationID)
  out.write("""# RECORD LARGEST AND SMALLEST DAILY RANGES (MAX-MIN) FOR STATION NUMBER  %s
     JAN     FEB     MAR     APR     MAY     JUN     JUL     AUG     SEP     OCT     NOV     DEC
 DY  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN\n""" % (stationID,) )

  rs = mydb.query("SELECT * from %s WHERE station = '%s'" \
   % (constants.climatetable(stationID), stationID,) ).dictresult()
  for i in range(len(rs)):
    day = mx.DateTime.strptime(rs[i]["valid"], "%Y-%m-%d")
    r[day] = rs[i]
 
  for day in range(1,32):
    out.write("%3i" % (day,) )
    for mo in range(1,13):
      try:
        ts = mx.DateTime.DateTime(2000, mo, day)
      except:
        out.write("  **  **")
        continue
      out.write("%4i%4i" % (r[ts]["max_range"], r[ts]["min_range"]) )
    out.write("\n")

