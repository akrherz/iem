# Generate 30 largest rainfalls

import constants
import mx.DateTime

def write(mydb, out, station):
    out.write("""# Top 30 single day rainfalls
 MONTH  DAY  YEAR   AMOUNT
""")

    rs = mydb.query("""SELECT precip, day from %s WHERE station = '%s' 
   and day >= '%s-01-01' ORDER by precip DESC LIMIT 30""" % (
        constants.get_table(station), station, 
        constants.startyear(station) ) ).dictresult()

    for i in range(len(rs)):
        ts = mx.DateTime.strptime(rs[i]["day"], "%Y-%m-%d")
        out.write("%4i%7i%6i%9.2f\n" % (ts.month, ts.day, ts.year, rs[i]["precip"]) )

