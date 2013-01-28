#!/usr/bin/env python

import re
from pyIEM import iemdb, mesonet
i = iemdb.iemdb()
mydb = i["portfolio"]

lines = open("times.txt", 'r').readlines()

emails = {}
bad = 0
for line in lines:
  t = line.split("|")
  sid = t[0]
  #if sid in ('SALI4', 'SAGI4','SLOI4'):
  #  print "Skip Mallard"
  #  continue
  sname = t[1]
  dur = float(t[2])
  if (not mesonet.kcciBack.has_key(sid)):
    continue
  if (dur < 1000):
    continue
  sql = "SELECT email from iem_site_contacts WHERE portfolio = 'kccisnet' \
         and s_mid = '%s'" % (sid, )
  rs = mydb.query(sql).dictresult()
  for i in range(len(rs)):
    emails[ rs[i]['email'] ] = 1
  print sname, dur
  bad += 1

for k in emails.keys():
  print "%s," % (k,),

print bad
