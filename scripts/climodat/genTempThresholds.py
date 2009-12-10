# Generate a report of daily occurances of temperature thresholds...

_REPORTID = "26"

def write(mydb, stationID):
  import constants, mx.DateTime
  out = open("reports/%s_%s.txt" % (stationID, _REPORTID), 'w')
  constants.writeheader(out, stationID)
  out.write("""# Number of days exceeding given temperature thresholds
# -20, -10, 0, 32 are days with low temperature at or below value
# 50, 70, 80, 93, 100 are days with high temperature at or above value
""")
  out.write("%s %4s %4s %4s %4s %4s %4s %4s %4s %4s\n" % (
      'YEAR', -20, -10, 0, 32, 50, 70, 80, 93, 100) )

  rs = mydb.query("""SELECT year, 
   sum(case when low <= -20 THEN 1 ELSE 0 END) as m20,
   sum(case when low <= -10 THEN 1 ELSE 0 END) as m10,
   sum(case when low <=  0 THEN 1 ELSE 0 END) as m0,
   sum(case when low <=  32 THEN 1 ELSE 0 END) as m32,
   sum(case when high >= 50 THEN 1 ELSE 0 END) as e50,
   sum(case when high >= 70 THEN 1 ELSE 0 END) as e70,
   sum(case when high >= 80 THEN 1 ELSE 0 END) as e80,
   sum(case when high >= 93 THEN 1 ELSE 0 END) as e93,
   sum(case when high >= 100 THEN 1 ELSE 0 END) as e100
   from alldata WHERE stationid = '%s' 
   and day >= '%s-01-01' GROUP by year ORDER by year ASC"""  % (
   stationID, constants.startyear(stationID) ) ).dictresult()

  for i in range(len(rs)):
    out.write("%(year)4i %(m20)4i %(m10)4i %(m0)4i %(m32)4i %(e50)4i %(e70)4i %(e80)4i %(e93)4i %(e100)4i\n" % rs[i] )

  out.close()
