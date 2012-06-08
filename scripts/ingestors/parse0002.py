""" 
  Quick and Dirty to get the ISUMET station data into the DB
"""
import mx.DateTime
import re
import os
import sys
import access
import pg
iemaccess = pg.connect('iem', 'iemdb')
now = mx.DateTime.now()
fp = now.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/text/ot/ot0002.dat")

if not os.path.isfile(fp):
  sys.exit(0)

iem = access.Ob("OT0002", "OT")

lines = open(fp, "r").readlines()

lastLine = lines[-1]

tokens = re.split("[\s+]+", lastLine)

tparts = re.split(":", tokens[4])
valid = now + mx.DateTime.RelativeDateTime(hour= int(tparts[0]), 
  minute = int(tparts[1]), second = int(tparts[2]) )

iem.data['valid'] = valid
iem.data['year'] = valid.year

sped = float(tokens[8])
sknt = round(sped *  0.868976, 1)

iem.data['sknt'] = sknt
iem.data['drct'] = tokens[9]
iem.data['tmpf'] = tokens[7]

iem.updateDatabase(iemaccess)

#mydb.query("SELECT zero_record('OT0002')")
#mydb.query("UPDATE current SET tmpf = %s, indoor_tmpf = %s, valid = '%s', \
#  sknt = %s, drct = %s WHERE station = '%s'" % (tokens[7], tokens[6], \
#  valid, tokens[8], tokens[9], "OT0002") )
