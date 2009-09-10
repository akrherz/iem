#!/mesonet/python/bin/python
# Daily Records Printout
# Daryl Herzmann 3 Mar 2004

_REPORTID = "05"

def write(mydb, stationID):
  import mx.DateTime, constants
  r = {}
  out = open("reports/%s_%s.txt" % (stationID, _REPORTID), 'w')
  constants.writeheader(out, stationID)
  out.write("""# DAILY MAXIMUM PRECIPITATION FOR STATION NUMBER %s 
     JAN   FEB   MAR   APR   MAY   JUN   JUL   AUG   SEP   OCT   NOV   DEC\n""" % (stationID,) )
  
  rs = mydb.query("SELECT * from %s WHERE station = '%s'" \
   % (constants.climatetable(stationID), stationID) ).dictresult()
  for i in range(len(rs)):
    day = mx.DateTime.strptime(rs[i]["valid"], "%Y-%m-%d")
    r[day] = rs[i]

  for day in range(1,32):
    out.write("%3i" % (day,) )
    for mo in range(1,13):
      try:
        ts = mx.DateTime.DateTime(2000, mo, day)
      except:
        out.write("  ****")
        continue
      out.write("%6.2f" % (r[ts]["max_precip"]) )
    out.write("\n")
  
