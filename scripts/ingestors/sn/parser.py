# Archive SN GRlevelx files

import sys, re, mx.DateTime, pg, urllib2, os

gmt = mx.DateTime.gmt()
fp = "http://www.spotternetwork.org/feeds/grlevelx.txt"
try:
  data = urllib2.urlopen( fp ).read()
except IOError:
  sys.exit()

o = open("/tmp/sn.txt", 'w')
o.write( data )
o.close()

cmd = "/home/ldm/bin/pqinsert -p 'data a %s bogus text/sn/gr_%s.txt txt' /tmp/sn.txt" % (gmt.strftime("%Y%m%d%H%M"), gmt.strftime("%Y%m%d%H%M"))
os.system(cmd)
