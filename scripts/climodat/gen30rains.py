# Generate 30 largest rainfalls

_REPORTID = "02"

def write(mydb, stationID):
  import constants, mx.DateTime
  out = open("reports/%s_%s.txt" % (stationID, _REPORTID), 'w')
  constants.writeheader(out, stationID)
  out.write("""# Top 30 single day rainfalls
 MONTH  DAY  YEAR   AMOUNT\n""")

  rs = mydb.query("SELECT precip, day from alldata WHERE stationid = '%s' \
   and day >= '%s-01-01' ORDER by precip DESC LIMIT 30" \
   % (stationID, constants.startyear(stationID) ) ).dictresult()

  for i in range(len(rs)):
    ts = mx.DateTime.strptime(rs[i]["day"], "%Y-%m-%d")
    out.write("%4i%7i%6i%9.2f\n" % (ts.month, ts.day, ts.year, rs[i]["precip"]) )

  out.close()
