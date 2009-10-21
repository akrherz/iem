# Generate Monthly averages
# Daryl Herzmann 4 Mar 2004

def go(mydb, stationID):
  import mx.DateTime, constants
  s = constants.startts(stationID)
  e = constants._ENDTS
  interval = mx.DateTime.RelativeDateTime(months=+1)

  now = s
  db = {}
  while (now < e):
    db[now] = {}
    now += interval

  rs = mydb.query("SELECT year, month, avg(high) as avg_high, \
    avg(low) as avg_low, sum(precip) as rain, \
    sum( CASE WHEN precip >= 0.01 THEN 1 ELSE 0 END ) as rcount, \
    sum( CASE WHEN snow >= 0.01 THEN 1 ELSE 0 END ) as scount from alldata \
    WHERE stationid = '%s' and day >= '%s-01-01' GROUP by year, month" \
     % (stationID, constants.startyear(stationID) ) ).dictresult()

  for i in range(len(rs)):
    ts = mx.DateTime.DateTime( int(rs[i]["year"]), int(rs[i]["month"]), 1)
    sql = "UPDATE r_monthly SET avg_high = %s, avg_low = %s, \
     rain = %s, rain_days = %s, snow_days = %s \
     WHERE stationid = '%s' and monthdate = '%s' " \
     % (rs[i]["avg_high"], rs[i]["avg_low"], rs[i]["rain"], rs[i]["rcount"], \
        rs[i]['scount'], stationID, ts.strftime("%Y-%m-%d") ) 
    #try:
    mydb.query(sql)
    #except:
    #  print sql


def safePrint(val, cols, prec):
  fmt = "%%%s.%sf" % (cols, prec)
  fmt2 = "%%%ss" % (cols,)
  if (val == "M"):
    return fmt2 % val
  return fmt % val

def write(mydb, stationID):
  import constants, mx.DateTime
  s = constants.startts(stationID)
  e = constants._ENDTS
  YRCNT = constants.yrcnt(stationID)
  YEARS = e.year - s.year + 1
  interval = mx.DateTime.RelativeDateTime(months=+1)

  now = s
  db = {}
  while (now < e):
    db[now] = {"avg_high": "M", "avg_low": "M", "rain": "M"}
    now += interval

  rs = mydb.query("SELECT * from r_monthly WHERE stationid = '%s'" \
   % (stationID,) ).dictresult()

  for i in range(len(rs)):
    ts = mx.DateTime.strptime(rs[i]["monthdate"], "%Y-%m-%d")
    if (ts < constants._ARCHIVEENDTS):
      db[ts] = rs[i]


  _REPORTID = "14"
  out = open("reports/%s_%s.txt" % (stationID, _REPORTID), 'w')
  constants.writeheader(out, stationID)
  out.write("""# Monthly Average High Temperatures [F]
YEAR   JAN   FEB   MAR   APR   MAY   JUN   JUL   AUG   SEP   OCT   NOV   DEC   ANN\n""")

  moTot = {}
  for mo in range(1,13):
    moTot[mo] = 0
  yrCnt = 0
  yrAvg = 0
  for yr in range(constants.startyear(stationID), constants._ENDYEAR):
    yrCnt += 1
    out.write("%4i" % (yr,) )
    yrSum = 0
    for mo in range(1, 13):
      ts = mx.DateTime.DateTime(yr, mo, 1)
      if (ts < constants._ARCHIVEENDTS):
        moTot[mo] += int(db[ts]["avg_high"])
        yrSum += int(db[ts]["avg_high"])
      out.write( safePrint( db[ts]["avg_high"], 6, 0) )
    if yr != constants._ARCHIVEENDTS.year:
      yrAvg += float(yrSum) / 12.0
      out.write("%6.0f\n" % ( float(yrSum) / 12.0, ) )
    else:
      out.write("      \n")

  out.write("MEAN")
  for mo in range(1,13):
    moAvg = moTot[mo] / float( YRCNT[mo])
    out.write("%6.0f" % (moAvg,) )

  out.write("%6.0f\n" % (yrAvg / (float(YEARS)),) )
  out.close()



  _REPORTID = "15"
  out = open("reports/%s_%s.txt" % (stationID, _REPORTID), 'w')
  constants.writeheader(out, stationID)
  out.write("""# Monthly Average Low Temperatures [F]
YEAR   JAN   FEB   MAR   APR   MAY   JUN   JUL   AUG   SEP   OCT   NOV   DEC   ANN\n""")

  moTot = {}
  for mo in range(1,13):
    moTot[mo] = 0
  yrCnt = 0
  yrAvg = 0
  for yr in range(constants.startyear(stationID), constants._ENDYEAR):
    yrCnt += 1
    out.write("%4i" % (yr,) )
    yrSum = 0
    for mo in range(1, 13):
      ts = mx.DateTime.DateTime(yr, mo, 1)
      if (ts < constants._ARCHIVEENDTS):
        moTot[mo] += int(db[ts]["avg_low"])
        yrSum += int(db[ts]["avg_low"])
      out.write( safePrint( db[ts]["avg_low"], 6, 0) )
    if yr != constants._ARCHIVEENDTS.year:
      yrAvg += float(yrSum) / 12.0
      out.write("%6.0f\n" % ( float(yrSum) / 12.0, ) )
    else:
      out.write("     M\n")

  out.write("MEAN")
  for mo in range(1,13):
    moAvg = moTot[mo] / float( YRCNT[mo])
    out.write("%6.0f" % (moAvg,) )

  out.write("%6.0f\n" % (yrAvg / float(YEARS),) )
  out.close()

  _REPORTID = "16"
  out = open("reports/%s_%s.txt" % (stationID, _REPORTID), 'w')
  constants.writeheader(out, stationID)
  out.write("""# Monthly Average Temperatures [F] (High + low)/2
YEAR   JAN   FEB   MAR   APR   MAY   JUN   JUL   AUG   SEP   OCT   NOV   DEC   ANN\n""")

  moTot = {}
  for mo in range(1,13):
    moTot[mo] = 0
  yrCnt = 0
  yrAvg = 0
  for yr in range(constants.startyear(stationID), constants._ENDYEAR):
    yrCnt += 1
    out.write("%4i" % (yr,) )
    yrSum = 0
    for mo in range(1, 13):
      ts = mx.DateTime.DateTime(yr, mo, 1)
      if (ts >= constants._ARCHIVEENDTS):
        out.write("%6s" % ("M",))
        continue
      v = (float(db[ts]["avg_high"]) + float(db[ts]["avg_low"])) / 2.0
      if (ts < constants._ARCHIVEENDTS):
        moTot[mo] += v
        yrSum += v
      out.write("%6.0f" % ( v, ) )
    if yr != constants._ARCHIVEENDTS.year:
      yrAvg += float(yrSum) / 12.0
      out.write("%6.0f\n" % ( float(yrSum) / 12.0, ) )
    else:
      out.write("     M\n")

  out.write("MEAN")
  for mo in range(1,13):
    moAvg = moTot[mo] / float( YRCNT[mo] )
    out.write("%6.0f" % (moAvg,) )

  out.write("%6.0f\n" % (yrAvg / float(yrCnt),) )
  out.close()

  _REPORTID = "17"
  out = open("reports/%s_%s.txt" % (stationID, _REPORTID), 'w')
  constants.writeheader(out, stationID)
  out.write("""# Monthly Liquid Precip Totals [inches] (snow is melted)
YEAR   JAN   FEB   MAR   APR   MAY   JUN   JUL   AUG   SEP   OCT   NOV   DEC   ANN\n""")

  moTot = {}
  for mo in range(1,13):
    moTot[mo] = 0
  yrCnt = 0
  yrAvg = 0
  for yr in range(constants.startyear(stationID), constants._ENDYEAR):
    yrCnt += 1
    out.write("%4i" % (yr,) )
    yrSum = 0
    for mo in range(1, 13):
      ts = mx.DateTime.DateTime(yr, mo, 1)
      if (ts < constants._ARCHIVEENDTS):
        moTot[mo] += db[ts]["rain"]
        yrSum += db[ts]["rain"]
      out.write( safePrint( db[ts]["rain"], 6, 2) )
    if yr != constants._ARCHIVEENDTS.year:
      yrAvg += float(yrSum) 
      out.write("%6.2f\n" % ( float(yrSum), ) )
    else:
      out.write("     M\n")

  out.write("MEAN")
  for mo in range(1,13):
    moAvg = moTot[mo] / float( YRCNT[mo] )
    out.write("%6.2f" % (moAvg,) )

  out.write("%6.2f\n" % (yrAvg / float(YEARS -1) ,) )
  out.close()
