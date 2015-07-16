#!/usr/bin/env python
"""
Generate a PNG windrose based on the CGI parameters, called from

    htdocs/sites/dyn_windrose.phtml
    htdocs/sites/windrose.phtml
"""
import datetime
import numpy
from pyiem.plot import windrose
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
                            int(form["hour1"].value),
                            int(form["minute1"].value))
    ets = datetime.datetime(int(form["year2"].value),
                            int(form["month2"].value), int(form["day2"].value),
                            int(form["hour2"].value),
                            int(form["minute2"].value))
else:
    sts = datetime.datetime(1900, 1, 1)
    ets = datetime.datetime(2050, 1, 1)

if "hour1" in form and "hourlimit" in form:
    hours = numpy.array((int(form["hour1"].value),))
elif "hour1" in form and "hour2" in form and "hourrangelimit" in form:
    if sts.hour > ets.hour:  # over midnight
        hours = numpy.arange(sts.hour, 24)
        hours = numpy.append(hours, numpy.arange(0, ets.hour))
    else:
        hours = numpy.arange(sts.hour, ets.hour)
else:
    hours = numpy.arange(0, 24)

if "units" in form and form["units"].value in ['mph', 'kts', 'mps', 'kph']:
    units = form["units"].value
else:
    units = "mph"

if "month1" in form and "monthlimit" in form:
    months = numpy.array((int(form["month1"].value),))
else:
    months = numpy.arange(1, 13)

database = 'asos'
if form["network"].value in ('KCCI', 'KELO', 'KIMT'):
    database = 'snet'
elif form["network"].value in ('IA_RWIS'):
    database = 'rwis'
elif form["network"].value in ('ISUSM'):
    database = 'isuag'

try:
    nsector = int(form['nsector'].value)
except:
    nsector = 36

windrose(form["station"].value, database=database, sts=sts, ets=ets,
         months=months, hours=hours, units=units, nsector=nsector,
         justdata=("justdata" in form))
