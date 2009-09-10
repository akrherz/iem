# Count mininum lows
# (Did not match old climodat very well), hmmm
# Daryl Herzmann 3 Mar 2004
# 30 Mar 2004	Add support for 2005

_REPORTID = "08"

def write(mydb, stationID):
  import constants, mx.DateTime
  out = open("reports/%s_%s.txt" % (stationID, _REPORTID), 'w')
  constants.writeheader(out, stationID)
  out.write("""# OF DAYS EACH YEAR WHERE MIN >=32 F\n""")

  rs = mydb.query("SELECT year, count(low) from alldata WHERE \
    stationid = '%s' and low >= 32 and day >= '%s-01-01' \
    and year < %s GROUP by year" % (stationID, constants.startyear(stationID), constants._THISYEAR) ).dictresult()
  tot = 0
  d = {}
  for yr in range(constants.startyear(stationID), constants._THISYEAR):
    d[yr] = 0
  for i in range(len(rs)):
    tot += int(rs[i]["count"])
    d[ int(rs[i]["year"]) ] = int(rs[i]["count"])

  mean = tot / len(rs)

  for yr in range(constants.startyear(stationID), constants._THISYEAR):
    out.write("%s %3i\n" % (yr, d[yr]))

  #l1 = ""
  #l2 = ""
  #for yr in range(1991, constants._THISYEAR):
  #  l1 += "%5i" % (yr,)
  #  l2 += "%5i" % (d[yr],)

  #out.write(l1 +"\n")
  #out.write(l2 +"\n\n")

  out.write("MEAN %3i\n" % (mean,) )
  out.close()
