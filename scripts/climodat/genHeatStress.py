# Calculate Heat Stress
# Daryl Herzmann 3 Mar 2004
# 23 Apr 2004	The word 'HEAT INDEX' is probably not correctly applied
# 17 Jun 2004	Need to use the constants!

_REPORTID = "20"

def write(mydb, stationID):
  import constants, mx.DateTime
  out = open("reports/%s_%s.txt" % (stationID, _REPORTID), 'w')
  constants.writeheader(out, stationID)
  out.write("""# THESE ARE THE HEAT STRESS VARIABLES FOR STATION #  %s\n""" % (stationID,) )

  s = constants.startts(stationID)
  e = constants._ENDTS
  interval = mx.DateTime.RelativeDateTime(months=+1)

  monthlyCount = {}
  monthlyIndex = {}
  now = s
  while (now < e):
    monthlyCount[now] = 0
    monthlyIndex[now] = 0
    now += interval

  rs = mydb.query("SELECT year, month, high from alldata WHERE \
    stationid = '%s' and high > 86 and day >= '%s-01-01'" % (stationID, constants.startyear(stationID) ) ).dictresult()
  for i in range(len(rs)):
    ts = mx.DateTime.DateTime( int(rs[i]["year"]), int(rs[i]["month"]), 1)
    monthlyCount[ts] += 1
    monthlyIndex[ts] += ( int(rs[i]["high"]) - 86 )

  monthlyAveCnt = {}
  monthlyAveIndex = {}
  for mo in range(5, 10):
    monthlyAveCnt[mo] = 0
    monthlyAveIndex[mo] = 0

  out.write("""             # OF DAYS MAXT >86              ACCUMULATED (MAXT - 86 )
 YEAR   MAY  JUNE  JULY   AUG  SEPT TOTAL      MAY  JUNE  JULY   AUG  SEPT TOTAL\n""")

  yrCnt = 0
  for yr in range(constants.startyear(stationID), constants._ENDYEAR):
    yrCnt += 1
    out.write("%5s" % (yr,) )
    totCnt = 0
    for mo in range(5,10):
      ts = mx.DateTime.DateTime(yr,mo,1)
      if (ts >= constants._ARCHIVEENDTS):
        out.write("%6s" % ("M",) )
        continue
      totCnt += monthlyCount[ts]
      monthlyAveCnt[mo] += monthlyCount[ts]
      out.write("%6i" % ( monthlyCount[ts], ) )
    out.write("%6i   " % (totCnt,) )
    totInd = 0
    for mo in range(5,10):
      ts = mx.DateTime.DateTime(yr,mo,1)
      if (ts >= constants._ARCHIVEENDTS):
        out.write("%6s" % ("M",) )
        continue
      totInd += monthlyIndex[ts]
      monthlyAveIndex[mo] += monthlyIndex[ts]
      out.write("%6i" % ( monthlyIndex[ts], ) )
    out.write("%6i\n" % (totInd,) )

  out.write(" **************************************************************************************\n")

  out.write("MEANS")
  tot = 0
  for mo in range(5,10):
    val = float(monthlyAveCnt[mo]) / float(yrCnt)
    tot += val
    out.write("%6.1f" % (val, ) )
  out.write("%6.1f   " % (tot,) )
  tot = 0
  for mo in range(5,10):
    val = float(monthlyAveIndex[mo]) / float(yrCnt)
    tot += val
    out.write("%6.1f" % ( val , ) )
  out.write("%6.1f\n" % (tot,) )
  out.close()
