#!/usr/bin/env python
""" Soil Moisture Timeseries """
import sys
sys.path.insert(0, '/mesonet/www/apps/iemwebsite/scripts/lib')
import datetime
import numpy
import mesonet
import iemtz
#import cgitb
#cgitb.enable()

import network
nt = network.Table("ISUSM")

# Query out the CGI variables
import cgi
form = cgi.FieldStorage()
if ("year1" in form and "year2" in form and 
    "month1" in form and "month2" in form and
    "day1" in form and "day2" in form and
    "hour1" in form and "hour2" in form):
    sts = datetime.datetime(int(form["year1"].value), 
      int(form["month1"].value), int(form["day1"].value),
      int(form["hour1"].value), 0)
    ets = datetime.datetime(int(form["year2"].value), 
      int(form["month2"].value), int(form["day2"].value), 
      int(form["hour2"].value), 0)
    
station = form.getvalue('station', 'CAMI4')
if not nt.sts.has_key(station):
    print 'Content-type: text/plain\n'
    print 'ERROR'
    sys.exit(0)

import iemdb
import psycopg2.extras
ISUAG = iemdb.connect('isuag', bypass=True)
icursor = ISUAG.cursor(cursor_factory=psycopg2.extras.DictCursor)

sql = """SELECT * from sm_hourly WHERE 
    station = '%s' and valid BETWEEN '%s' and '%s' ORDER by valid ASC""" % (
            station, 
            sts.strftime("%Y-%m-%d %H:%M"), ets.strftime("%Y-%m-%d %H:%M"))
icursor.execute(sql)
d12sm = []
d24sm = []
d50sm = []
d12t = []
d24t = []
d50t = []
tair = []
tsoil = []
valid = []
slrkw = []
rain = []
for row in icursor:
    slrkw.append( row['slrkw_avg'] or numpy.nan)
    d12sm.append( row['vwc_12_avg'] or numpy.nan)
    d12t.append( row['t12_c_avg'] or numpy.nan)
    d24t.append( row['t24_c_avg'] or numpy.nan)
    d50t.append( row['t50_c_avg'] or numpy.nan)
    d24sm.append( row['vwc_24_avg'] or numpy.nan)
    d50sm.append( row['vwc_50_avg'] or numpy.nan)
    valid.append( row['valid'] )
    rain.append( row['rain_mm_tot'] or numpy.nan)
    tair.append( row['tair_c_avg'] or numpy.nan)
    tsoil.append( row['tsoil_c_avg'] or numpy.nan)

slrkw = numpy.array( slrkw )
rain = numpy.array( rain )
d12sm = numpy.array( d12sm )
d24sm = numpy.array( d24sm )
d50sm = numpy.array( d50sm )
d12t = numpy.array( d12t )
d24t = numpy.array( d24t )
d50t = numpy.array( d50t )
tair = numpy.array( tair )
tsoil = numpy.array( tsoil )

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

maxy = max( [numpy.max(d12sm), numpy.max(d24sm), numpy.max(d50sm)])
miny = min( [numpy.min(d12sm), numpy.min(d24sm), numpy.min(d50sm)])

(fig, ax) = plt.subplots(3,1, sharex=True, figsize=(7,10))
ax[0].grid(True)
ax2 = ax[0].twinx()
ax2.set_yticks( numpy.arange(-0.6, 0., 0.1))
ax2.set_yticklabels( 0 - numpy.arange(-0.6, 0.01, 0.1))
ax2.set_ylim(-0.6, 0)
ax2.set_ylabel("Hourly Precipitation [inch]")
ax2.bar(valid, 0 - rain / 25.4, width=0.04, fc='b', ec='b', zorder=1)

ax[0].plot(valid, d12sm * 100.0, linewidth=2, color='r', zorder=2, label='12 inch')
ax[0].plot(valid, d24sm * 100.0, linewidth=2, color='purple', zorder=2, label='24 inch')
ax[0].plot(valid, d50sm * 100.0, linewidth=2, color='black', zorder=2, label='50 inch')
ax[0].set_ylabel("Volumetric Soil Water Content [%]", fontsize=10)
ax[0].legend(loc=(0, -0.15), ncol=3)
ax[0].set_ylim(miny * 100.0 - 5, maxy * 100.0 + 5)

days = (ets - sts).days  
if days >= 3:
    interval = max(int(days/7), 1)
    ax[0].xaxis.set_major_locator(
                               mdates.DayLocator(interval=interval, tz=iemtz.Central)
                               )
    ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%-d %b\n%Y', tz=iemtz.Central))
else:
    ax[0].xaxis.set_major_locator(
                               mdates.AutoDateLocator(maxticks=10, tz=iemtz.Central)
                               )
    ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%-I %p\n%d %b',
                                                      tz=iemtz.Central))

ax[0].set_title("ISUAG Station: %s Timeseries" % (nt.sts[station]['name'],
                                            ))

ax[1].plot(valid, mesonet.c2f( d12t), linewidth=2, color='r', label='12in')
ax[1].plot(valid, mesonet.c2f( d24t), linewidth=2, color='purple', label='24in')
ax[1].plot(valid, mesonet.c2f( d50t), linewidth=2, color='black', label='50in')
ax[1].grid(True)
ax[1].set_ylabel(r"Temperature $^\circ$F")

ax[2].plot(valid, mesonet.c2f( tair ), linewidth=2, color='blue', zorder=2, 
           label='Air')
ax[2].plot(valid, mesonet.c2f( tsoil ), linewidth=2, color='red', zorder=2, 
           label='4" Soil')
ax[2].grid(True)
ax[2].legend(loc=(.1, 1.01), ncol=2)
ax[2].set_ylabel(r"Temperature $^\circ$F")

ax2 = ax[2].twinx()
ax2.plot(valid, slrkw * 1000.0, color='g')
ax2.set_ylabel("Solar Radiation [W/m^2]", color='g')

# Wow, strange bugs if I did not put this last
ax[0].set_xlim( min(valid), max(valid))
print "Content-Type: image/png\n"
plt.savefig( sys.stdout, format='png' )