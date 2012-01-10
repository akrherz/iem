
import mesonet, iemdb
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

import mx.DateTime


acursor.execute("SELECT valid, tmpf, dwpf from alldata WHERE station = 'DSM' and extract(month from valid) = 12 and extract(hour from valid) in (14,15,16,17) and tmpf > -50 and dwpf > -50 ORDER by valid ASC")
tot = 0
for row in acursor:
  tot += mesonet.relh(float(row[1]), float(row[2]))

print "%.2f" % (tot / float(acursor.rowcount),)
