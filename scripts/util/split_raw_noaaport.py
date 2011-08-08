#!/mesonet/python/bin/python

import mx.DateTime, os
from support import TextProduct

sts = mx.DateTime.DateTime(2011,5,1)
ets = mx.DateTime.DateTime(2011,6,1)
interval = mx.DateTime.RelativeDateTime(days=1)

now = sts
while(now < ets):
  out = open('%s.shef' % (now.strftime("%Y%m%d"),), 'w')
  os.system("tar -zxf /home/ldm/offline/text/%s.tgz" % (now.strftime("%Y%m%d"),))
  #for q in range(0,24):
  for q in range(8,15):
    print now, q
    fp = "%s%02i.txt" % (now.strftime("%d"), q)
    if not os.path.isfile(fp):
      print 'Missing', fp
      continue
    o = open(fp).read()
    prods = o.split("\003")
    del o
    for prod in prods:
      if (prod.find("EOKI4 ") < 0 and prod.find("DLDI4 ") < 0):
        continue
      try:
        p = TextProduct.TextProduct(prod)
      except:
        continue
      #if (p.afos is not None and p.afos[:3] in ['MET', 'MAV']):
      if (p.afos is not None and p.afos[:3] in ['RR3',]):
        out.write(prod +"\003")
    os.unlink("%s%02i.txt" % (now.strftime("%d"), q))
  out.close()
  now += interval
