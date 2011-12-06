# Compute mean depatures at or around a holiday

import mx.DateTime
import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

#climate = {}
#rs = coop.query("SELECT valid, high from climate where station = 'ia0200'").dictresult()
#for i in range(len(rs)):
#  climate[ rs[i]['valid'][5:] ] = rs[i]['high']

days = []
for yr in range(1900,2011):
  nov1 = mx.DateTime.DateTime(yr, 11, 1)
  turkey = nov1 + mx.DateTime.RelativeDateTime(weekday=(mx.DateTime.Thursday,4))
  sql = "SELECT day, high, low, case when precip > 0.005 THEN 1 else 0 end as precip, case when snow > 0.005 then 1 else 0 end as snow from alldata_ia WHERE station = '%s' and day <= '%s' ORDER by day DESC LIMIT 31" % ('IA0200', turkey )
  ccursor.execute( sql )
  first = None
  cnt = 0
  for row in ccursor:
    if first is None:
      first = row[1]
    else:
      high = row[1]
      if high < first:
        cnt += 1
      else:
        break
  days.append( cnt )

days.append(23)    

import matplotlib.pyplot as plt
import numpy

days = numpy.array( days )

fig = plt.figure()
ax = fig.add_subplot(111)

rects = ax.bar( numpy.arange(1900,2012) - 0.4, days, facecolor='b', edgecolor='b')
rects[-1].set_edgecolor('r')
rects[-1].set_facecolor('r')
ax.set_xlim(1899.5, 2012.5)
ax.set_ylabel("Days prior to Thanksgiving")
ax.set_title("Ames [1900-2011] Consecuative Days Prior to Thanksgiving\nwith a Cooler High Temperature than Thanksgiving")
ax.set_xlabel("Largest 1998: Thanksgiving 65$^{\circ}\mathrm{F}$, Oct 29th 72$^{\circ}\mathrm{F}$")
#ax.set_xticks( numpy.arange(1895,2015,5) )
ax.grid(True)

import iemplot
fig.savefig('test.ps')
iemplot.makefeature('test')

#for i in range(7):
#  print i, total_error[i] / 117.0, total_rain[i] / 117.0, total_snow[i] / 117.0
