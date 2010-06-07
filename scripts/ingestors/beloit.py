# Ingest Beloit Data

import mx.DateTime
from pyIEM import mesonet, iemAccessOb, iemAccess, iemAccessDatabase
iemdb = iemAccessDatabase.iemAccessDatabase()

dyfile = open('/mnt/home/mesonet/ot/ot0005/incoming/Beloit/BeloitDaily.dat', 'r').readlines()
lastline = dyfile[-1]
tokens = lastline.split(",")
stamp = tokens[0].replace('"', '')
ts = mx.DateTime.strptime(stamp, '%Y-%m-%d %H:%M:%S')
high = mesonet.c2f( float(tokens[2]) )
low = mesonet.c2f( float(tokens[3]) )
pday = float(tokens[4]) / 25.4
iemdb.query("UPDATE summary_%s SET max_tmpf = %s, min_tmpf = %s, pday = %s WHERE station = 'OT0009' and day = '%s'" % (ts.year, high, low, pday, ts.strftime("%Y-%m-%d")))

hrfile = open('/mnt/home/mesonet/ot/ot0005/incoming/Beloit/BeloitHourly.dat','r').readlines()

lastline = hrfile[-1]
tokens = lastline.split(",")
stamp = tokens[0].replace('"', '')
tmpf = mesonet.c2f( float(tokens[3]) )
relh = float(tokens[4])
if relh > 100: relh = 100
if relh < 0: relh = 0
srad = float(tokens[5])
if srad < 0: srad = 0
sknt = float(tokens[6]) * 2.0
drct = tokens[7]
phour = float(tokens[8]) / 25.4
c1tmpf = mesonet.c2f( float(tokens[9]) )
mslp = tokens[10]
reftemp = tokens[11]
voltage = tokens[12]

ts = mx.DateTime.strptime(stamp, '%Y-%m-%d %H:%M:%S') + mx.DateTime.RelativeDateTime(hours=6)

iemob = iemAccessOb.iemAccessOb("OT0009")
iemob.setObTimeGMT(ts)
iemob.data['tmpf'] = tmpf
iemob.data['dwpf'] = mesonet.dwpf(tmpf, relh)
iemob.data['relh'] = relh
iemob.data['sknt'] = sknt
iemob.data['drct'] = drct
iemob.data['phour'] = phour
iemob.data['mslp'] = mslp
iemob.data['c1tmpf'] = c1tmpf
iemob.data['srad'] = srad
iemob.updateDatabase(iemdb)



