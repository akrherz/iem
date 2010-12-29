# Ingest the Monkey's data

from pyIEM import iemAccessOb, iemAccess, mesonet, iemAccessDatabase
import mx.DateTime, sys, os

try:
  iemdb = iemAccessDatabase.iemAccessDatabase()
except:
  if (mx.DateTime.now().minute == 10):
    print "DATABASE FAIL"
  sys.exit(0)
iemob = iemAccessOb.iemAccessOb("OT0006")

fp = "/mesonet/ARCHIVE/data/%s/text/ot/ot0006.dat" % (mx.DateTime.now().strftime("%Y/%m/%d"),)

if (not os.path.isfile(fp)):
  if (mx.DateTime.now().minute == 10 and mx.DateTime.now().hour == 12):
    print "WHERE IS IEM2's DATA?"
  sys.exit(0)

lines = open(fp, 'r').readlines()

line = lines[-1]
if (len(line) < 20):
  sys.exit(0)

tokens = line.split()
# ['10', '28', '2004', '00', '38', '53.2', '53.2', '52.8', '94', '2', '176', '6', '12:02AM', '30.08', '0.00', '1.38', '1.38', '75.2', '54']
ts = mx.DateTime.DateTime( int(tokens[2]), int(tokens[0]), int(tokens[1]), int(tokens[3]), int(tokens[4]))

iemob.setObTime(ts)
iemob.data['tmpf'] = tokens[5]
iemob.data['relh'] = tokens[8]
iemob.data['dwpf'] = mesonet.dwpf(float(iemob.data['tmpf']), float(iemob.data['relh']) )
iemob.data['sknt'] = tokens[9]
iemob.data['drct'] = tokens[10]
iemob.data['pres'] = tokens[13]
iemob.data['pday'] = tokens[14]
iemob.data['gust'] = tokens[11]
iemob.updateDatabase(iemdb)

# Piggy Back
iemob = iemAccessOb.iemAccessOb("OT0007")

fp = "/mnt/a1/ARCHIVE/data/%s/text/ot/ot0007.dat" % (mx.DateTime.now().strftime("%Y/%m/%d"),)

if (not os.path.isfile(fp)):
  sys.exit(0)

lines = open(fp, 'r').readlines()

line = lines[-1]

# 114,2006,240,1530,18.17,64.70, 88.9,2.675,21.91,1014.3,0.000
tokens = line.split(",")
if (len(tokens) != 11):
  sys.exit(0)
hhmm = "%04i" % (int(tokens[3]),)
ts = mx.DateTime.now() + mx.DateTime.RelativeDateTime(hour= int(hhmm[:2]), minute= int(hhmm[2:]), second = 0 )

iemob.setObTime(ts)
iemob.data['tmpf'] = tokens[5]
iemob.data['relh'] = tokens[6]
iemob.data['dwpf'] = mesonet.dwpf(float(iemob.data['tmpf']), float(iemob.data['relh']) )
iemob.data['sknt'] = float(tokens[7]) * 1.94
iemob.data['drct'] = tokens[8]
iemob.data['pres'] = float(tokens[9]) / 960 * 28.36
iemob.updateDatabase(iemdb)

