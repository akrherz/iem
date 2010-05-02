
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

o = open("/tmp/awos_adas.txt", 'w')
o.write("\n".join(data) )
o.close()

si, so = os.popen4("/home/ldm/bin/pqinsert -p 'data a %s bogus text/adas/%s.txt bogus' /tmp/awos_adas.txt" % (archivets.strftime("%Y%m%d%H%M"), archivets.strftime("%Y%m%d%H%M") ) )

os.unlink("/tmp/awos_adas.txt")
