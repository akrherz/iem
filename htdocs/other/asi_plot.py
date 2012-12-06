#!/usr/bin/env python
""" ASI Data Timeseries """
import sys
sys.path.insert(0, '/mesonet/www/apps/iemwebsite/scripts/lib')
import os
os.environ[ 'HOME' ] = '/tmp/'
os.environ[ 'USER' ] = 'nobody'
import datetime
import numpy
import sys
import iemtz
import cgitb
cgitb.enable()

import network
nt = network.Table("ISUASI")

# Query out the CGI variables
import cgi
form = cgi.FieldStorage()
if ("syear" in form and "eyear" in form and 
    "smonth" in form and "emonth" in form and
    "sday" in form and "eday" in form and
    "shour" in form and "ehour" in form):
    sts = datetime.datetime(int(form["syear"].value), 
      int(form["smonth"].value), int(form["sday"].value),
      int(form["shour"].value), 0)
    ets = datetime.datetime(int(form["eyear"].value), 
      int(form["emonth"].value), int(form["eday"].value), 
      int(form["ehour"].value), 0)
    
station = form.getvalue('station', 'ISU4003')
if not nt.sts.has_key(station):
    print 'Content-type: text/plain\n'
    print 'ERROR'
    sys.exit(0)

import iemdb
import psycopg2.extras
ISUAG = iemdb.connect('other', bypass=True)
icursor = ISUAG.cursor(cursor_factory=psycopg2.extras.DictCursor)

sql = """SELECT * from asi_data WHERE 
    station = '%s' and valid BETWEEN '%s' and '%s' ORDER by valid ASC""" % (
            station, 
            sts.strftime("%Y-%m-%d %H:%M"), ets.strftime("%Y-%m-%d %H:%M"))
icursor.execute(sql)
ch1avg = []
ch2avg = []
ch3avg = []
valid = []
for row in icursor:
    ch1avg.append( row['ch1avg'] )
    ch2avg.append( row['ch3avg'] )
    ch3avg.append( row['ch5avg'] )
    valid.append( row['valid'] )

ch1avg = numpy.array( ch1avg )
ch2avg = numpy.array( ch2avg )
ch3avg = numpy.array( ch3avg )

import matplotlib.pyplot as plt
import matplotlib.dates as mdates


(fig, ax) = plt.subplots(1,1)
ax.grid(True)

ax.plot(valid, ch1avg, linewidth=2, color='r', zorder=2, label='48.5m')
ax.plot(valid, ch2avg, linewidth=2, color='purple', zorder=2, label='32m')
ax.plot(valid, ch3avg, linewidth=2, color='black', zorder=2, label='10m')
ax.set_ylabel("Wind Speed [m/s]")
ax.legend(loc=(0, 0.01), ncol=3)
ax.set_xlim( min(valid), max(valid))
days = (ets - sts).days  
if days >= 3:
    interval = max(int(days/7), 1)
    ax.xaxis.set_major_locator(
                               mdates.DayLocator(interval=interval)
                               )
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b\n%Y'))
else:
    ax.xaxis.set_major_locator(
                               mdates.AutoDateLocator(maxticks=10)
                               )
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%-I %p\n%d %b',
                                                      tz=iemtz.Central))

ax.set_title("ISUASI Station: %s Timeseries" % (nt.sts[station]['name'],
                                            ))


print "Content-Type: image/png\n"
plt.savefig( sys.stdout, format='png' )