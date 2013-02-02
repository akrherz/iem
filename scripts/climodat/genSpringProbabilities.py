# Compute Frost Probabilities!
# Daryl Herzmann 1 Sep 2005

import mx.DateTime
import constants

def write(mydb, out, station):

    # Load up dict of dates..
    cnt = {}
    for day in range(30,183):
        cnt[day] = {32: 0.0, 28: 0.0, 26: 0.0, 22: 0.0}
    cnt_years = {32: 0.0, 28: 0.0, 26: 0.0, 22: 0.0}

    for base in (32,28,26,22):
        # Query Last doy for each year in archive
        sql = "select year, max(extract(doy from day)) as doy from %s \
           WHERE month < 7 and low <= %s and low > -40 and station = '%s' \
           and year >= %s and year < %s and month > 1 \
         GROUP by year ORDER by doy ASC" % (constants.get_table(station), base, station, constants.startyear(station), constants._ENDYEAR)
        rs = mydb.query(sql).dictresult()
        cnt_years[base] = len(rs)
        if (len(rs) == 0):
            return
        for i in range(len(rs)):
            cnt[ int(rs[i]['doy']) ][base] += 1.0

    sts = mx.DateTime.DateTime(2000,1,1)
    running = {32: 0.0, 28: 0.0, 26: 0.0, 22: 0.0}
    out.write("""# Low Temperature exceedence probabilities
# (On a certain date, what is the chance a temperature below a certain
# threshold will be observed again that spring)
 DOY Date    <33  <29  <27  <23
""")
    ar = []
    for day in range(181,29,-1):
        ts = sts + mx.DateTime.RelativeDateTime(days=day-1)
        for base in (32,28,26,22):
            running[base] += cnt[day][base]
        if (day % 2 == 0):
            ar.append(" %3s %s  %3i  %3i  %3i  %3i" % (ts.strftime("%-j"),
              ts.strftime("%b %d"), 
              running[32] / cnt_years[32] * 100.0,
              running[28] / cnt_years[28] * 100.0,
              running[26] / cnt_years[26] * 100.0,
              running[22] / cnt_years[22] * 100.0 ))

    ar.reverse()
    out.write( "\n".join(ar) )
