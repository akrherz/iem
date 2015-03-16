"""
 Need something to ingest the CTRE provided bridge data
  RSAI4
  RLRI4
 Run from RUN_1MIN
"""

import datetime
import sys
import pytz
import pyiem.util as util
# Run every 3 minutes
now = datetime.datetime.now()
if now.minute % 4 != 0 and len(sys.argv) < 2:
    sys.exit(0)

from pyiem.observation import Observation
props = util.get_properties()
import urllib2
import psycopg2
import subprocess
IEM = psycopg2.connect(database='iem', host='iemdb')
icursor = IEM.cursor()

csv = open('/tmp/ctre.txt', 'w')

# Get Saylorville
try:
    req = urllib2.Request(("ftp://%s:%s@129.186.224.167/Saylorville_"
                           "Table3Min_current.dat"
                           "") % (props['ctre_ftpuser'],
                                  props['ctre_ftppass']))
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
    d[keys[i]] = vals[i]

# Ob times are always CDT
ts1 = datetime.datetime.strptime(d['TIMESTAMP'], '%Y-%m-%d %H:%M:%S')
gts1 = ts1 + datetime.timedelta(hours=5)
gts1 = gts1.replace(tzinfo=pytz.timezone("UTC"))
lts = gts1.astimezone(pytz.timezone("America/Chicago"))

iem = Observation('RSAI4', "OT", lts)
drct = d['WindDir']
iem.data['drct'] = drct
sknt = float(d['WS_mph_S_WVT']) / 1.15
iem.data['sknt'] = sknt
gust = float(d['WS_mph_Max']) / 1.15
iem.data['gust'] = gust
iem.save(icursor)

csv.write("%s,%s,%s,%.1f,%.1f\n" % ('RSAI4',
                                    gts1.strftime("%Y/%m/%d %H:%M:%S"),
                                    drct, sknt, gust))

# Red Rock
try:
    req = urllib2.Request(("ftp://%s:%s@129.186.224.167/Red Rock_Table3"
                           "Min_current.dat") % (props['ctre_ftpuser'],
                                                 props['ctre_ftppass']))
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
    d[keys[i]] = vals[i]

ts2 = datetime.datetime.strptime(d['TIMESTAMP'], '%Y-%m-%d %H:%M:%S')
gts2 = ts2 + datetime.timedelta(hours=5)
gts2 = gts2.replace(tzinfo=pytz.timezone("UTC"))
lts = gts2.astimezone(pytz.timezone("America/Chicago"))

iem = Observation('RLRI4', "OT", lts)
drct = d['WindDir']
iem.data['drct'] = drct
sknt = float(d['WS_mph_S_WVT']) / 1.15
iem.data['sknt'] = sknt
gust = float(d['WS_mph_Max']) / 1.15
iem.data['gust'] = gust
iem.save(icursor)

csv.write("%s,%s,%s,%.1f,%.1f\n" % ('RLRI4',
                                    gts2.strftime("%Y/%m/%d %H:%M:%S"),
                                    drct, sknt, gust))

csv.close()

cmd = ("/home/ldm/bin/pqinsert -i -p 'data c %s csv/ctre.txt "
       "bogus txt' /tmp/ctre.txt") % (now.strftime("%Y%m%d%H%M"),)
subprocess.call(cmd, shell=True)

icursor.close()
IEM.commit()
IEM.close()
