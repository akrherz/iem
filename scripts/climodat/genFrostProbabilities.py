# Compute Frost Probabilities!
# Daryl Herzmann 1 Sep 2005


_REPORTID = "22"

def write(mydb, stationid):
    import mx.DateTime, constants
    out = open("reports/%s_%s.txt" % (stationid, _REPORTID), 'w')
    constants.writeheader(out, stationid)

    # Load up dict of dates..
    cnt = {}
    for day in range(210,366):
        cnt[day] = {32: 0.0, 28: 0.0, 26: 0.0, 22: 0.0}
    cnt_years = {32: 0.0, 28: 0.0, 26: 0.0, 22: 0.0}

    for base in (32,28,26,22):
        # Query Last doy for each year in archive
        sql = "select year, min(extract(doy from day)) as doy from alldata \
           WHERE month > 7 and low <= %s and low > -40 and stationid = '%s' \
           GROUP by year ORDER by doy ASC" % (base, stationid,)
        rs = mydb.query(sql).dictresult()
        cnt_years[base] = len(rs)
        for i in range(len(rs)):
            cnt[ int(rs[i]['doy']) ][base] += 1.0

    sts = mx.DateTime.DateTime(2000,1,1)
    running = {32: 0.0, 28: 0.0, 26: 0.0, 22: 0.0}
    out.write("""# Low Temperature exceedence probabilities
# (On a certain date, what is the chance a temperature below a certain
#  threshold would have been observed once already during the fall of that year)
 DOY Date    <33  <29  <27  <23
""")
    for day in range(230,366):
        ts = sts + mx.DateTime.RelativeDateTime(days=day-1)
        for base in (32,28,26,22):
            running[base] += cnt[day][base]
        if (day % 2 == 0):
            out.write(" %3s %s  %3i  %3i  %3i  %3i\n" % (ts.strftime("%-j"),
              ts.strftime("%b %d"), running[32] / cnt_years[base] * 100.0,
              running[28] / cnt_years[base] * 100.0,
              running[26] / cnt_years[base] * 100.0,
              running[22] / cnt_years[base] * 100.0 ))

    out.close()

if (__name__ == '__main__'):
    from pyIEM import iemdb
    i = iemdb.iemdb()
    coop = i['coop']
    write(coop, 'ia0112')
