# I love writting data converters
# Daryl Herzmann 16 Jul 2003

import re, mx.DateTime, string
import sys
ST = sys.argv[1]
from pyIEM import stationTable, iemdb
i = iemdb.iemdb()
coopdb = i['coop']
coopdb.query("BEGIN;")

o = open("%s_dat.txt" % (ST,), 'r').readlines()
s = mx.DateTime.DateTime(1930,1,1)
e = mx.DateTime.DateTime(1970,1,1)
interval = mx.DateTime.RelativeDateTime(days=+1)

data = {}

for line in o[2:]:
  tokens = re.split(",", line)
  month = mx.DateTime.strptime(tokens[7], "%Y%m")
  var = tokens[5]
  coopid = "%s%s" % (ST.lower(), str(tokens[1][2:]))
  sid = coopid
  if (not data.has_key(sid)):
    data[sid] = {}
  for i in range(31):
    p = 9 + (i*4)
    val = tokens[p]
    ts = month + mx.DateTime.RelativeDateTime(day=(i+1))
    if (not data[sid].has_key(ts)):
      data[sid][ts] = {'TMAX':'Null', 'TMIN':'Null', 'SNOW':'Null', 'PRCP':'Null', 'SNWD': 'Null'}
    data[sid][ts][var] = val
    if (tokens[p+1] == "T"):
      #print "HERE"
      data[sid][ts][var] = 0.001

now = s
cnt = 0
while (now < e):
  for sid in data.keys():
    if not data[sid].has_key(now):
      continue
    if (data[sid][now]["TMAX"] != 'Null'):
      high = int(float(data[sid][now]["TMAX"]))
      if (high < -100 or high > 140):  
        high = 'Null'
        cnt += 1
    else:  
      high = data[sid][now]["TMAX"]
      cnt += 1

    if (data[sid][now]["TMIN"] != 'Null'):
      low = int(float(data[sid][now]["TMIN"]))  
      if (low < -100 or low > 100):  
        low = 'Null'
        cnt += 1
    else:
      low = data[sid][now]["TMIN"]
      cnt += 1

    if (data[sid][now]["PRCP"] != 'Null'):
      precip = int(float(data[sid][now]["PRCP"])) /100.0
      if (precip < 0 or precip > 100):
        precip = 'Null'
        cnt += 1
    else:
      precip =  data[sid][now]["PRCP"]
      cnt += 1

    if (data[sid][now]["SNOW"] != 'Null'):
      snow = int(float(data[sid][now]["SNOW"]))  /10.0
      if (snow < 0 or snow > 30):
        snow = 'Null'
        cnt += 1
    else:
      snow = data[sid][now]["SNOW"]
      cnt += 1

    if (data[sid][now]["SNWD"] != 'Null'):
      snowd = int(float(data[sid][now]["SNWD"]))
      if (snowd < 0 or snowd > 30):
        snowd = 'Null'
        cnt += 1
    else:
      snowd = 'Null'
      cnt += 1

    sql = "INSERT into alldata_%s (stationid, day, high, low, precip, snow, \
           sday, year, month,snowd) values ('%s','%s',%s,%s,%s,%s,'%s',%s,%s,%s) "\
           % (ST.lower(), sid.lower(), now.strftime("%Y-%m-%d"), high, low, precip, snow,\
           now.strftime("%m%d"), now.year, now.month, snowd)
    #sql = "UPDATE alldata SET snow = %s WHERE stationid = '%s' and day = '%s'" % (snow, sid.lower(), now.strftime("%Y-%m-%d"))
    #print sql
    #if (snow > 0):
    coopdb.query(sql)
    #print "%s,%s" % (now.strftime("%Y-%m-%d"), evap)

  now = now + interval

coopdb.query("COMMIT;")
print "Missing values", cnt
