# Daily Records Printout
# Daryl Herzmann 3 Mar 2004

import mx.DateTime
import constants

def write(mydb, out, station):
    r = {}
    out.write("""# DAILY RECORD HIGHS AND LOWS OCCURRING DURING %s-%s FOR STATION NUMBER  %s
     JAN     FEB     MAR     APR     MAY     JUN     JUL     AUG     SEP     OCT     NOV     DEC
 DY  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN
""" % (constants.startyear(station), constants._ENDYEAR, station) )
  
    rs = mydb.query("SELECT * from %s WHERE station = '%s'" % (
            constants.climatetable(station), station) ).dictresult()
    for i in range(len(rs)):
        day = mx.DateTime.strptime(rs[i]["valid"], "%Y-%m-%d")
        r[day] = rs[i]

    for day in range(1,32):
        out.write("%3i" % (day,) )
        for mo in range(1,13):
            try:
                ts = mx.DateTime.DateTime(2000, mo, day)
            except:
                out.write(" *** ***")
                continue
            out.write("%4i%4i" % (r[ts]["max_high"], r[ts]["min_low"]) )
        out.write("\n")
  
