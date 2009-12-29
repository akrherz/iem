#!/mesonet/python/bin/python
# Process the current RAWS ob for IEM processing
# Daryl Herzmann 13 Jun 2003
# 17 Jun 2003	Account for when the file is blank
# 19 Jun 2003	Now we insert into DB instead of silly CSV files
# 30 Jun 2003	Is day == 1 a problem?  I am not sure, since we are already 
#		using GMT to initialize mx.DateTime
# 16 Sep 2003	Use iemAccess site stuff

import sys, mx.DateTime, string
from pyIEM import iemdb, iemAccess, iemAccessOb
iemaccess = iemAccess.iemAccess()
i = iemdb.iemdb()
mydb = i["other"]
mydb.query("SET TIME ZONE 'GMT'")

now = mx.DateTime.gmt()

f = open(sys.argv[1], 'r').readlines()

if (len(f) == 0):
  sys.exit(0)

dl = f[1]

day = int(dl[25:27])
hr  = int(dl[28:30])
mi  = int(dl[30:32])

tmpf = -99
if (string.strip(dl[35:38]) != "MM"):
  tmpf = int(dl[35:38])
dwpf = -99
if (string.strip(dl[39:42]) != "MM"):
  dwpf = int(dl[39:42])
wind = dl[43:47]
pcpn = dl[49:55]
relh = dl[57:60]
peak = dl[67:73]
srad = dl[87:91]

if (wind[2:] == "MM"):
  sknt = "-99"
else:
  sknt = int(wind[2:])
if (wind[:2] == "MM"):
  drct = "-99"
else:
  drct = int(wind[:2]) * 10

#if (day == 1):
#  now = now 

now = now + mx.DateTime.RelativeDateTime(second=0, minute=mi, hour=hr)

if (peak[:3] == " MM"):
  gustDir = "-99"
else:
  gustDir = int(peak[:3]) * 10
if (peak[4:] == "MM"):
  gust = "-99"
else:
  gust = peak[4:]

sid = sys.argv[2]

iemob = iemAccessOb.iemAccessOb(sid)
iemob.data['tmpf'] = tmpf
iemob.data['sknt'] = sknt
iemob.data['dwpf'] = dwpf
iemob.data['drct'] = drct
iemob.setObTimeGMT(now)
iemob.updateDatabase(iemaccess.iemdb)

try:
  mydb.query("INSERT into t%s (station, valid, tmpf, dwpf, sknt, drct) VALUES \
    ('%s', '%s', %s, %s, %s, %s)" % (now.year, sid, now, tmpf, dwpf, sknt, drct) )
except:
  ha = 'ha'
