#!/usr/bin/env python

import netCDF4
import datetime
import sys
import cgi
import os
import numpy

print 'Content-type: text/plain \n'

form = cgi.FormContent()

hrap_i = 20147
if (form.has_key("hrap")):
    hrap_i = int(form["hrap"][0])

if (form.has_key("syear") and form.has_key("smonth") and form.has_key("sday")):
    sts = datetime.datetime(int(form["syear"][0]), int(form["smonth"][0]), 
                            int(form["sday"][0]) )
else:
    sts = datetime.datetime.now() - datetime.timedelta(days=1)
    sts = sts.replace(hour=0,minute=0)

if (form.has_key("eyear") and form.has_key("emonth") and form.has_key("eday")):
    ets = datetime.datetime(int(form["eyear"][0]), int(form["emonth"][0]), \
                               int(form["eday"][0]) )
else:
    ets = datetime.datetime.now()
    ets = ets.replace(hour=0,minute=0)

gx = (hrap_i - 1) % 173
gy = (hrap_i - 1) / 173
year = 2004

interval = datetime.timedelta(days=1)

now = sts 
while now < ets:
    # Get GMT rep
    fp = now.strftime("/wepp/data/rainfall/netcdf/daily/%Y/%m/%Y%m%d_rain.nc")
    if (os.path.isfile(fp)):
        nc = netCDF4.Dataset(fp, 'r')
        p = nc.variables["rainfall_15min"]
    else:
        p = numpy.zeros( (96,134,173), 'f' )
    for i in range(96):
        minutes = (i + 1) * 15
        print "%s %s" % (
                (now + datetime.timedelta(seconds=minutes*60)).strftime(
                                "%Y-%m-%d %H:%M"), p[i][gy][gx] )
    del(p)
    if (os.path.isfile(fp)):
        del(nc)
    now += interval
