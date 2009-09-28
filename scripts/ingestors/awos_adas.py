
import datetime, urllib2
import shutil, os, sys
from pyIEM import awosOb

archivets = datetime.datetime.utcnow()

req = urllib2.Request("ftp://rwis:rwisftp1@165.206.203.34/AWOS.DAT")
try:
  data = urllib2.urlopen(req).readlines()
except:
  sys.exit(0)

# output file
dmx = open('metar.dat', 'w')
dmx.write("""000 
SAUS70 KXXX %s
METAR
""" % (archivets.strftime("%d%H%M"), ) )
# 228 bytes per ob
for line in data:
  packet = line.replace(",","")
  ob = awosOb.awosOb(packet)
  ob.calc()

  ob.printMetar(dmx, "")

dmx.close()

# Send to LDM
cmd = "/home/ldm/bin/pqinsert -p 'data c %s iaawos.txt bogus bogus' metar.dat" % (archivets.strftime("%Y%m%d%H%M"),)
os.system(cmd)

# Archive it
dir = "/mesonet/ARCHIVE/raw/awos/adas/%s" % (archivets.strftime("%Y/%m/%d/"), )
if (not os.path.isdir(dir)):
  os.makedirs(dir)

fp = "%s/%s_raw.txt" % (dir, archivets.strftime("%H%M"), )
o = open(fp, 'w')
o.write("\n".join(data) )
o.close()
