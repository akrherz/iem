# GDD module
# Daryl Herzmann 4 Mar 2004

_REPORTID = "03"

def cgdd(base, high, low):
  gdd = 0
  if (high > 86): high = 86
  if (low < base): low = base
  if (high < base): high = base
  a = float(high + low) / 2.0
  gdd = a - base
  return gdd  

def go(mydb, rs, stationID):
  import mx.DateTime, constants
  s = constants.startts(stationID)
  e = constants._ENDTS
  interval = mx.DateTime.RelativeDateTime(months=+1)

  now = s
  db = {}
  while (now < e):
    db[now] = {40: 0, 48: 0, 50: 0, 52: 0}
    now += interval

  for i in range(len(rs)):
    ts = mx.DateTime.strptime( rs[i]["day"] , "%Y-%m-%d")
    mo = ts + mx.DateTime.RelativeDateTime(day=1) # First of month
    for base in (40,48,50,52):
      db[mo][base] += cgdd(base, rs[i]["high"], rs[i]["low"])

#  mydb.query("DELETE from r_gdd WHERE stationID = '%s'" \
#   % (stationID,) )
  for mo in db.keys():
    mydb.query("UPDATE r_monthly SET gdd40 = %s, gdd48 = %s, \
      gdd50 = %s, gdd52 = %s WHERE stationid = '%s' and monthdate = '%s'" % \
      (db[mo][40], db[mo][48], \
      db[mo][50], db[mo][52], stationID, mo.strftime("%Y-%m-%d") ) )

def write(mydb, stationID):
  import mx.DateTime, constants
  out = open("reports/%s_%s.txt" % (stationID, _REPORTID), 'w')
  constants.writeheader(out, stationID)
  out.write("# GROWING DEGREE DAYS FOR 4 BASE TEMPS FOR STATION ID  %s \n" \
   % (stationID,) )

  rs = mydb.query("SELECT * from r_monthly WHERE stationid = '%s'" \
   % (stationID,) ).dictresult()
  db = {}
  for i in range(len(rs)):
    mo = mx.DateTime.strptime( rs[i]["monthdate"], "%Y-%m-%d")
    db[mo] = {40: rs[i]["gdd40"], 48: rs[i]["gdd48"], 50: rs[i]["gdd50"], \
              52: rs[i]["gdd52"]}

  rs = mydb.query("SELECT avg(gdd40) as avg_gdd40, stddev(gdd40) as std_gdd40,\
    avg(gdd48) as avg_gdd48, stddev(gdd48) as std_gdd48, \
    avg(gdd50) as avg_gdd50, stddev(gdd50) as std_gdd50, \
    avg(gdd52) as avg_gdd52, stddev(gdd52) as std_gdd52, \
    extract(month from monthdate) as month from r_monthly \
    WHERE stationid = '%s' GROUP by month" % (stationID,) ).dictresult()
  adb = {}
  for i in range(len(rs)):
    month = int(rs[i]["month"])
    adb[month] = {'a40': rs[i]["avg_gdd40"], 's40': rs[i]["std_gdd40"], \
     'a48': rs[i]["avg_gdd48"], 's48': rs[i]["std_gdd48"], \
     'a50': rs[i]["avg_gdd50"], 's50': rs[i]["std_gdd50"], \
     'a52': rs[i]["avg_gdd52"], 's52': rs[i]["std_gdd52"] }



  modMonth(stationID, out, db, adb, 3, 4, "MARCH", "APRIL")
  modMonth(stationID, out, db, adb, 5, 6, "MAY", "JUNE")
  modMonth(stationID, out, db, adb, 7, 8, "JULY", "AUGUST")
  modMonth(stationID, out, db, adb, 9, 10, "SEPTEMBER", "OCTOBER")
  out.close()

def modMonth(stationID, out, db, adb, mo1, mo2, mt1, mt2):
  import mx.DateTime, constants
  out.write("""\n               %-12s                %-12s
     ****************************  *************************** 
 YEAR  40-86  48-86  50-86  52-86   40-86  48-86  50-86  52-86  
     ****************************  *************************** \n""" \
   % (mt1, mt2))
  s = constants.startts(stationID)
  e = constants._ARCHIVEENDTS
  interval = mx.DateTime.RelativeDateTime(years=+1)
  now = s
  while (now < e):
    m1 = now + mx.DateTime.RelativeDateTime(month=mo1)
    m2 = now + mx.DateTime.RelativeDateTime(month=mo2)
    if (m1 >= constants._ARCHIVEENDTS):
      db[m1] = {40: 'M', 48: 'M', 50: 'M', 52: 'M'}
    if (m2 >= constants._ARCHIVEENDTS):
      db[m2] = {40: 'M', 48: 'M', 50: 'M', 52: 'M'}
    out.write("%5i%7s%7s%7s%7s%7s%7s%7s%7s\n" % (now.year, \
     db[m1][40], db[m1][48], db[m1][50], db[m1][52], \
     db[m2][40], db[m2][48], db[m2][50], db[m2][52]) )
    now += interval

  out.write("     ****************************  ****************************\n")
  out.write(" MEAN%7.1f%7.1f%7.1f%7.1f%7.1f%7.1f%7.1f%7.1f\n" \
   % (adb[mo1]["a40"], adb[mo1]["a48"], adb[mo1]["a50"], adb[mo1]["a52"], \
   adb[mo2]["a40"], adb[mo2]["a48"], adb[mo2]["a50"], adb[mo2]["a52"]) )
  out.write(" STDV%7.1f%7.1f%7.1f%7.1f%7.1f%7.1f%7.1f%7.1f\n" \
   % (adb[mo1]["s40"], adb[mo1]["s48"], adb[mo1]["s50"], adb[mo1]["s52"], \
   adb[mo2]["s40"], adb[mo2]["s48"], adb[mo2]["s50"], adb[mo2]["s52"]) )
