# Ingest Beloit Data

import mx.DateTime
from pyIEM import mesonet, iemAccessOb, iemAccess, iemAccessDatabase
iemdb = iemAccessDatabase.iemAccessDatabase()

hrfile = open('/mnt/home/mesonet/ot/ot0005/incoming/Beloit/BeloitHourly.dat','r').readlines()

lastline = hrfile[-1]
tokens = lastline.split(",")
stamp = tokens[0].replace('"', '')
tmpf = mesonet.c2f( float(tokens[3]) )
rh = float(tokens[4])
if rh > 100: rh = 100
if rh < 0: rh = 0
srad = float(tokens[5])
if srad < 0: srad = 0
sknt = float(tokens[6]) * 2.0
drct = tokens[7]
phour = float(tokens[8]) / 25.4
c1tmpf = mesonet.c2f( float(tokens[9]) )
mslp = tokens[10]
reftemp = tokens[11]
voltage = tokens[12]

ts = mx.DateTime.strptime(stamp, '%Y-%m-%d %H:%M:%S')

iemob = iemAccessOb.iemAccessOb("OT0009")
iemob.setObTime(ts)
iemdb.data['tmpf'] = tmpf
iemdb.data['dwpf'] = mesonet.dwpf(tmpf, relh)
iemob.data['sknt'] = sknt
iemob.data['drct'] = drct
iemob.data['phour'] = phour
iemob.data['mslp'] = mslp
iemob.data['c1tmpf'] = c1tmpf
iemob.data['srad'] = srad
iemob.updateDatabase(iemdb)



