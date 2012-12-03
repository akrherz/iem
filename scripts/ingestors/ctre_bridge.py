"""
 Need something to ingest the CTRE provided bridge data
  RSAI4
  RLRI4
 Run from RUN_1MIN
"""

import mx.DateTime
import sys
# Run every 3 minutes
now = mx.DateTime.now()
if now.minute % 4 != 0 and len(sys.argv) < 2:
    sys.exit(0)

import urllib2
import csv
import access
import secret
import subprocess
import iemdb
IEM = iemdb.connect('iem')
icursor = IEM.cursor()

csv = open('/tmp/ctre.txt', 'w')

# Get Saylorville
try:
    req = urllib2.Request("ftp://%s:%s@129.186.224.167/Saylorville_Table3Min_current.dat" % (secret.CTRE_FTPUSER,
                                                        secret.CTRE_FTPPASS))
    data = urllib2.urlopen(req, timeout=30).readlines()
except:
    if now.minute % 15 == 0:
        print 'Download CTRE Bridge Data Failed!!!'
    sys.exit(0)
if len(data) < 2:
    sys.exit(0)
keys = data[0].strip().replace('"', '').split(',')
vals = data[1].strip().replace('"', '').split(',')
d = {}
for i in range(len(vals)):
    d[ keys[i] ] = vals[i]

# Ob times are always CDT
ts1 = mx.DateTime.strptime(d['TIMESTAMP'], '%Y-%m-%d %H:%M:%S')
gts1 = ts1 + mx.DateTime.RelativeDateTime(hours=5)

iem = access.Ob( 'RSAI4', "OT")
iem.setObTimeGMT( gts1 )
drct = d['WindDir']
iem.data['drct'] = drct
sknt = float(d['WS_mph_S_WVT']) / 1.15
iem.data['sknt'] = sknt
gust = float(d['WS_mph_Max']) / 1.15
iem.data['gust'] = gust
iem.updateDatabase( cursor=icursor )

csv.write("%s,%s,%s,%.1f,%.1f\n" % ('RSAI4', 
            gts1.strftime("%Y/%m/%d %H:%M:%S"),
      drct, sknt, gust) )


# Red Rock
try:
    req = urllib2.Request("ftp://%s:%s@129.186.224.167/Red Rock_Table3Min_current.dat" % (secret.CTRE_FTPUSER,
                                                        secret.CTRE_FTPPASS))
    data = urllib2.urlopen(req, timeout=30).readlines()
except:
    if now.minute % 15 == 0:
        print 'Download CTRE Bridge Data Failed!!!'
    sys.exit(0)

if len(data) < 2:
    sys.exit(0)
#except:
#  pass
keys = data[0].strip().replace('"', '').split(',')
vals = data[1].strip().replace('"', '').split(',')
d = {}
for i in range(len(vals)):
    d[ keys[i] ] = vals[i]

ts2 = mx.DateTime.strptime(d['TIMESTAMP'], '%Y-%m-%d %H:%M:%S')
gts2 = ts2 + mx.DateTime.RelativeDateTime(hours=5)

iem = access.Ob( 'RLRI4', "OT")
iem.setObTimeGMT( gts2 )
drct = d['WindDir']
iem.data['drct'] = drct
sknt = float(d['WS_mph_S_WVT']) / 1.15
iem.data['sknt'] = sknt
gust = float(d['WS_mph_Max']) / 1.15
iem.data['gust'] = gust
iem.updateDatabase( cursor=icursor)

csv.write("%s,%s,%s,%.1f,%.1f\n" % ('RLRI4', 
            gts2.strftime("%Y/%m/%d %H:%M:%S"),
      drct, sknt, gust) )

csv.close()

cmd = "/home/ldm/bin/pqinsert -p 'data c 000000000000 csv/ctre.txt bogus txt' /tmp/ctre.txt >& /dev/null"
if ((mx.DateTime.gmt() - gts1).seconds > 3600. and
   (mx.DateTime.gmt() - gts2).seconds > 3600.):
    sys.exit()
subprocess.call( cmd, shell=True )

icursor.close()
IEM.commit()
IEM.close()
