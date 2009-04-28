#!/mesonet/python/bin/python
# Wiz bang to extract precip for a given hrap_i and year
# Daryl Herzmann 22 Jun 2004
# 9 Feb 2004  We need to finish this bad boy!

from Scientific.IO import NetCDF
import sys, mx.DateTime, cgi, datetime, os, Numeric

print 'Content-type: text/plain \n'

form = cgi.FormContent()

hrap_i = 20147
if (form.has_key("hrap")):
  hrap_i = int(form["hrap"][0])

if (form.has_key("syear") and form.has_key("smonth") and form.has_key("sday")):
  sts = mx.DateTime.DateTime(int(form["syear"][0]), int(form["smonth"][0]), \
    int(form["sday"][0]) )
else:
  sts = mx.DateTime.now() + mx.DateTime.RelativeDateTime(days=-1,hour=0,minute=0)

if (form.has_key("eyear") and form.has_key("emonth") and form.has_key("eday")):
  ets = mx.DateTime.DateTime(int(form["eyear"][0]), int(form["emonth"][0]), \
    int(form["eday"][0]) )
else:
  ets = mx.DateTime.now() + mx.DateTime.RelativeDateTime(hour=0,minute=0)

gx = (hrap_i - 1) % 173
gy = (hrap_i - 1) / 173
year = 2004

interval = mx.DateTime.RelativeDateTime(days=+1)

now = sts 
while (now < ets):
  # Get GMT rep
  gmt = datetime.datetime.utcfromtimestamp( now.ticks() )
  fp = gmt.strftime("/wepp/data/rainfall/netcdf/daily/%Y/%m/%Y%m%d_rain.nc")
  if (os.path.isfile(fp)):
    nc = NetCDF.NetCDFFile(fp, 'r')
    p = nc.variables["rainfall_15min"]
  else:
    p = Numeric.zeros( (96,134,173), Numeric.Float )
  for i in range(96):
    minutes = (i + 1) * 15
    print "%s %s" % \
 ((now + mx.DateTime.RelativeDateTime(minutes=minutes)).strftime("%Y-%m-%d %H:%M"), p[i][gy][gx] )
  del(p)
  if (os.path.isfile(fp)):
    del(nc)
  now += interval
