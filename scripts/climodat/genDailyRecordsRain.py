import constants
import mx.DateTime

def write(mydb, out, station):
    r = {}
    out.write("""# DAILY MAXIMUM PRECIPITATION FOR STATION NUMBER %s 
     JAN   FEB   MAR   APR   MAY   JUN   JUL   AUG   SEP   OCT   NOV   DEC
""" % (station,) )
  
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
                out.write("  ****")
                continue
            out.write("%6.2f" % (r[ts]["max_precip"]) )
        out.write("\n")
  
