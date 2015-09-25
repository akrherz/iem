# Daily Records Printout

import mx.DateTime
import constants


def write(mydb, out, station):
    r = {}
    out.write("""# DAILY RECORD HIGHS AND LOWS OCCURRING DURING %s-%s FOR STATION NUMBER  %s
     JAN     FEB     MAR     APR     MAY     JUN     JUL     AUG     SEP     OCT     NOV     DEC
 DY  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN
""" % (constants.startyear(station), constants._ENDYEAR, station))

    rs = mydb.query("SELECT * from %s WHERE station = '%s'" % (
            constants.climatetable(station), station)).dictresult()
    for i in range(len(rs)):
        day = mx.DateTime.strptime(rs[i]["valid"], "%Y-%m-%d")
        r[day] = rs[i]

    for day in range(1, 32):
        out.write("%3i" % (day,))
        for mo in range(1, 13):
            try:
                ts = mx.DateTime.DateTime(2000, mo, day)
                if ts not in r:
                    print ("Records missing for table: %s station: %s "
                           "date: %s") % (constants.climatetable(station),
                                          station, ts.strftime("%b %d"))
                    out.write(" *** ***")
                    continue
            except:
                out.write(" *** ***")
                continue
            if (r[ts]['max_high'] is None or
                    r[ts]['min_low'] is None):
                out.write(" *** ***")
                continue
            out.write("%4i%4i" % (r[ts]["max_high"], r[ts]["min_low"]))
        out.write("\n")
