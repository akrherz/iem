#!/usr/bin/env python

import mx.DateTime
from Scientific.IO import NetCDF
from pyIEM import iemdb
i = iemdb.iemdb()
coop = i['coop']

nc = NetCDF.NetCDFFile("ia2203.nc")

ts0 = mx.DateTime.DateTime( nc.variables["byear"].getValue(), nc.variables["bmonth"].getValue(),1)
tsend = mx.DateTime.DateTime( 1951, 1, 1)

maxt = nc.variables['maxt']
mint = nc.variables['mint']
pcpn = nc.variables['pcpn']
snow = nc.variables['snow']
snwg = nc.variables['snwg']

now = ts0
while (now < tsend):
  iyear = now.year - ts0.year
  imonth = now.month - 1
  iday = now.day - 1

  high = maxt[iyear,imonth,iday][0]
  if high < -50 or high > 130:
    high = "Null"
  low = mint[iyear,imonth,iday][0]
  if low < -50 or low > 100:
    low = "Null"
  pday = pcpn[iyear,imonth,iday][0] / 100.0
  if pday < 0 or pday > 100:
    pday = "Null"
  sday = snow[iyear,imonth,iday][0] / 10.0
  if sday < 0 or sday > 100:
    sday = "Null"
  snowd = snwg[iyear,imonth,iday][0]
  if snowd < 0 or snowd > 100:
    snowd = "Null"

  sql = "INSERT into alldata_tmp (year, month, stationid, sday, day, high, low, precip, snow, snowd) values (%s, %s, '%s', '%s', '%s', %s, %s, %s, %s, %s)" % (now.year, now.month, 'ia2203', now.strftime("%m%d"), now.strftime("%Y-%m-%d"), high, low, pday, sday, snowd)
  coop.query(sql)

  now += mx.DateTime.RelativeDateTime(days=1)
