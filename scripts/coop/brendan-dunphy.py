#!/usr/bin/env python

import mx.DateTime
from pyIEM import iemdb
i = iemdb.iemdb()
coopdb = i['coop']

sts = mx.DateTime.DateTime(2013,5,27)
ets = mx.DateTime.DateTime(2013,7,8)
interval = mx.DateTime.RelativeDateTime(days=7)

now = sts
while (now < ets):
  e = now + interval
#  sql = "SELECT avg(precip) * 7 as d from alldata WHERe stationid IN \
#        (SELECT distinct stationid from alldata WHERE precip > 0 and \
#         year = 2007) and day >= '%s' and day < '%s'" % ( \
#         now.strftime("%Y-%m-%d"), e.strftime("%Y-%m-%d") )
#  sql = "SELECT avg(precip) * 7 as d from alldata WHERe stationid IN \
#        ('ia0200') and day >= '%s' and day < '%s'" % ( \
#         now.strftime("%Y-%m-%d"), e.strftime("%Y-%m-%d") )
  sql = """SELECT avg(high) as h, avg(low) as l, sum(precip) as p 
         from alldata_ia WHERe station IN 
        ('IA0000') and day >= '%s' and day < '%s'""" % ( 
         now.strftime("%Y-%m-%d"), e.strftime("%Y-%m-%d") )
  rs = coopdb.query(sql).dictresult()
  print "%s,%.1f,%.1f,%.2f" % ( now.strftime("%Y-%m-%d"), rs[0]['h'], 
       rs[0]['l'], rs[0]['p'] )

  now += interval
