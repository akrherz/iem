# Need something to ingest the CTRE provided bridge data
# RSAI4
# RLRI4

import mx.DateTime
import sys
# Run every 3 minutes
if mx.DateTime.now().minute % 3 != 0:
    sys.exit(0)

import urllib2
import csv
import access
import pg
import secret
import os
accessdb = pg.connect('iem', 'iemdb')

csv = open('/tmp/ctre.txt', 'w')

# Get Saylorville
req = urllib2.Request("ftp://%s:%s@129.186.224.167/Saylorville_Table3Min_current.dat" % (secret.CTRE_FTPUSER,
                                                        secret.CTRE_FTPPASS))
#try:
data = urllib2.urlopen(req).readlines()
#except:
#  pass
keys = data[0].strip().replace('"', '').split(',')
vals = data[1].strip().replace('"', '').split(',')
d = {}
for i in range(len(vals)):
    d[ keys[i] ] = vals[i]

ts1 = mx.DateTime.strptime(d['TIMESTAMP'], '%Y-%m-%d %H:%M:%S')

iem = access.Ob( 'RSAI4', "OT")
iem.setObTime( ts1 )
drct = d['WindDir']
iem.data['drct'] = drct
sknt = float(d['WS_mph_S_WVT']) / 1.15
iem.data['sknt'] = sknt
gust = float(d['WS_mph_Max']) / 1.15
iem.data['gust'] = gust
iem.updateDatabase( accessdb )

csv.write("%s,%s,%s,%.1f,%.1f\n" % ('RSAI4', 
            ts1.gmtime().strftime("%Y/%m/%d %H:%M:%S"),
      drct, sknt, gust) )


# Get Saylorville
req = urllib2.Request("ftp://%s:%s@129.186.224.167/Red Rock_Table3Min_current.dat" % (secret.CTRE_FTPUSER,
                                                        secret.CTRE_FTPPASS))
#try:
data = urllib2.urlopen(req).readlines()
#except:
#  pass
keys = data[0].strip().replace('"', '').split(',')
vals = data[1].strip().replace('"', '').split(',')
d = {}
for i in range(len(vals)):
    d[ keys[i] ] = vals[i]

ts2 = mx.DateTime.strptime(d['TIMESTAMP'], '%Y-%m-%d %H:%M:%S')

iem = access.Ob( 'RLRI4', "OT")
iem.setObTime( ts2 )
drct = d['WindDir']
iem.data['drct'] = drct
sknt = float(d['WS_mph_S_WVT']) / 1.15
iem.data['sknt'] = sknt
gust = float(d['WS_mph_Max']) / 1.15
iem.data['gust'] = gust
iem.updateDatabase( accessdb )

csv.write("%s,%s,%s,%.1f,%.1f\n" % ('RLRI4', 
            ts2.gmtime().strftime("%Y/%m/%d %H:%M:%S"),
      drct, sknt, gust) )

csv.close()

cmd = "/home/ldm/bin/pqinsert -p 'data c 000000000000 csv/ctre.txt bogus txt' /tmp/ctre.txt"
if ((mx.DateTime.now() - ts1).seconds > 3600. and
   (mx.DateTime.now() - ts2).seconds > 3600.):
    sys.exit()
os.system( cmd )