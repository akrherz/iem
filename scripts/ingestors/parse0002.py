# Quick and Dirty to get the ISUMET station data into the DB
# Daryl Herzmann 19 Jun 2003
# 18 Aug 2003	Add in iemAccess support

import mx.DateTime, re, os, sys
from pyIEM import iemAccessDatabase, iemAccessOb
try:
  iemdb = iemAccessDatabase.iemAccessDatabase()
except:
  if (mx.DateTime.now().minute == 10):
    print "DATABASE FAIL"
  sys.exit(0)


now = mx.DateTime.now()
fp = now.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/text/ot/ot0002.dat")

if (not os.path.isfile(fp)):
  sys.exit(0)

iem = iemAccessOb.iemAccessOb("OT0002")

lines = open(fp, "r").readlines()

lastLine = lines[-1]

tokens = re.split("[\s+]+", lastLine)

tparts = re.split(":", tokens[4])
valid = now + mx.DateTime.RelativeDateTime(hour= int(tparts[0]), \
  minute = int(tparts[1]), second = int(tparts[2]) )

iem.data['ts'] = valid
iem.data['year'] = valid.year

sped = float(tokens[8])
sknt = round(sped *  0.868976, 1)

iem.data['sknt'] = sknt
iem.data['drct'] = tokens[9]
iem.data['tmpf'] = tokens[7]

iem.updateDatabase(iemdb)

#mydb.query("SELECT zero_record('OT0002')")
#mydb.query("UPDATE current SET tmpf = %s, indoor_tmpf = %s, valid = '%s', \
#  sknt = %s, drct = %s WHERE station = '%s'" % (tokens[7], tokens[6], \
#  valid, tokens[8], tokens[9], "OT0002") )
