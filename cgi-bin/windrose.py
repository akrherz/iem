#!/mesonet/python/bin/python

import sys
sys.path.insert(0, '/var/www/scripts/lib')
import os
os.environ[ 'HOME' ] = '/tmp/'
os.environ[ 'USER' ] = 'nobody'
import datetime
import numpy
import cgitb
cgitb.enable()

# Query out the CGI variables
import cgi
form = cgi.FieldStorage()
if ("year1" in form and "year2" in form and 
    "month1" in form and "month2" in form and
    "day1" in form and "day2" in form and
    "hour1" in form and "hour2" in form and
    "minute1" in form and "minute2" in form):
    sts = datetime.datetime(int(form["year1"].value), 
      int(form["month1"].value), int(form["day1"].value),
      int(form["hour1"].value), int(form["minute1"].value))
    ets = datetime.datetime(int(form["year2"].value), 
      int(form["month2"].value), int(form["day2"].value), 
      int(form["hour2"].value), int(form["minute2"].value))
else:
    sts = datetime.datetime(1900,1,1)
    ets = datetime.datetime(2050,1,1)

if "hour1" in form and "hourlimit" in form:
    hours = numpy.array( (int(form["hour1"].value),) )
else:
    hours = numpy.arange(0,24)

if "month1" in form and "monthlimit" in form:
    months = numpy.array( (int(form["month1"].value),) )
else:
    months = numpy.arange(1,13)

database = 'asos'
if form["network"].value in ('KCCI','KELO','KIMT'):
    database = 'snet'
if form["network"].value in ('IA_RWIS'):
    database = 'rwis'

import iemplot
iemplot.windrose(form["station"].value, database=database,sts=sts, ets=ets, months=months, hours=hours)
