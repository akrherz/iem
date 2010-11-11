"""
Compute out the peak ASOS rainfall intensities, since we have this fancy
1 minute archive going
"""

import iemdb
import numpy
import datetime
ASOS = iemdb.connect("asos", bypass=True)
IEM = iemdb.connect("iem", bypass=True)
acursor = ASOS.cursor()
icursor = IEM.cursor()

tot = [0]*11
for yr in range(2000,2011):
    # Query out the rainfall events
    cnt = 0
    icursor.execute("""select distinct date(valid), station from hourly_"""+`yr`+"""
    WHERE network = 'IA_ASOS' and phour > 0.05""")
    for row in icursor:
        # Now we go look for rainfall data
        acursor.execute("""SELECT valid, precip from t"""+`yr`+"""_1minute where
      valid >= %s and valid < %s + '36 hours'::interval 
      and station = %s and precip > 0  and precip < 0.3
      """, (row[0], row[0],
      row[1]))
        ts0 = datetime.datetime(row[0].year, row[0].month, row[0].day)
        data = numpy.zeros( (2160,), 'f')
        for row2 in acursor:
            ts1 = datetime.datetime(row2[0].year, row2[0].month, row2[0].day, row2[0].hour, row2[0].minute)
            offset = ((ts1 - ts0).days * 1440) + ((ts1 - ts0).seconds / 60)
            data[offset] = row2[1]
        # Shortcut
        if max(data) < 0.05:
            continue
        i = 120
        for k in range(0,2160-i+1):
            s = sum( data[k:k+i] )
            if s >= 2.:
                cnt += 1
                print "NEW Station: %s Time: %s Val: %.2f" % (
                  row[1], ts0 + datetime.timedelta(minutes=k), s) 
                break

    tot[yr-2000] = cnt

print tot
