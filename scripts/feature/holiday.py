# Compute mean depatures at or around a holiday

import mx.DateTime
import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

#climate = {}
#rs = coop.query("SELECT valid, high from climate where station = 'ia0200'").dictresult()
#for i in range(len(rs)):
#  climate[ rs[i]['valid'][5:] ] = rs[i]['high']

#total_error = [0]*7
#total_rain = [0]*7
#total_snow = [0]*7
highs = []
lows = []
for yr in range(1978,2010):
  nov1 = mx.DateTime.DateTime(yr, 11, 1)
  turkey = nov1 + mx.DateTime.RelativeDateTime(weekday=(mx.DateTime.Thursday,4))
  sql = "SELECT day, high, low, case when precip > 0.005 THEN 1 else 0 end as precip, case when snow > 0.005 then 1 else 0 end as snow from alldata WHERE stationid = '%s' and day = '%s'" % ('ia2203', turkey )
  ccursor.execute( sql )
  row = ccursor.fetchone()
  highs.append( row[1] )
  lows.append( row[2] )

highs.append( 25 )
lows.append( 18 )

import matplotlib.pyplot as plt
import numpy

h = numpy.array( highs )
l = numpy.array( lows )

fig = plt.figure(1, figsize=(8,8))
ax = fig.add_subplot(111)

def mod_rects( rects ):
	for rect in rects:
		if (rect.get_y() + rect.get_height()) < 32:
			rect.set_facecolor('b')

rects = ax.bar( numpy.arange(1978,2011) - 0.4, h - l, bottom=l, facecolor='r' )
mod_rects( rects )
ax.set_xlim(1977.5, 2010.5)
ax.set_xlabel("Year, * 2010 Data Forecasted")
ax.set_title("Des Moines Thanksgiving High & Low Temperature")
ax.set_ylabel("Temperature $^{\circ}\mathrm{F}$")
#ax.set_xticks( numpy.arange(1895,2015,5) )
ax.grid(True)

import iemplot
fig.savefig('test.ps')
iemplot.makefeature('test')

#for i in range(7):
#  print i, total_error[i] / 117.0, total_rain[i] / 117.0, total_snow[i] / 117.0
