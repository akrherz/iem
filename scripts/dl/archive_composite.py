# Cache NEXRAD composites for the website

import urllib2, os, mx.DateTime, time, random
from pyIEM import iemdb
i = iemdb.iemdb()
postgis = i['postgis']

opener = urllib2.build_opener()

def save(sectorName, file_name, dir_name, tstamp,bbox=None):
  layers = "layers[]=nexrad&layers[]=watch_by_county&layers[]=sbw&layers[]=uscounties"
  #layers = "layers[]=nexrad&layers[]=county_warnings&layers[]=watches&layers[]=uscounties"
  #layers = "layers[]=nexrad&layers[]=watches&layers[]=uscounties"
  uri = "http://iem50.local/GIS/radmap.php?sector=%s&ts=%s&%s" % \
        (sectorName,tstamp, layers)
  if (bbox is not None):
    uri = "http://iem50.local/GIS/radmap.php?bbox=%s&ts=%s&%s" % \
        (bbox,tstamp, layers)

  try:
    f = opener.open(uri)
  except:
    time.sleep(5)
    f = opener.open(uri)
  o = open('atmp.png', 'w')
  o.write( f.read() )
  o.close()

  cmd = "/home/ldm/bin/pqinsert -p 'plot a %s %s %s/n0r_%s_%s.png png' atmp.png" % (tstamp, file_name, dir_name, tstamp[:8], tstamp[8:])
  os.system(cmd)

"""
# 1995 JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC
# 1996 JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC
# 1997 JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC
# 1998 JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC
# 1999 JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC
# 2000 JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC
# 2001 JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC
# 2002 JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC
"""

sts = mx.DateTime.DateTime(2010,5,29,0,0)
ets = mx.DateTime.DateTime(2010,5,29,8,0)
interval = mx.DateTime.RelativeDateTime(minutes=5)
now = sts
while (now < ets):
  #if now.hour == 0 and now.minute == 0:
  #  time.sleep( 300 )  # 5 minute break
  #print now
  s = now.strftime("%Y%m%d%H%M")
  save('conus', 'uscomp.png', 'usrad', s)
  save('iem', 'mwcomp.png', 'comprad', s)
  for i in ['lot','ict','sd','hun']:
    save(i, '%scomp.png'%(i,), '%srad' %(i,), s)
  now += interval
