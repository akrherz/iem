import iemdb
import mx.DateTime
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("select high, max(sday) from (select day, sday, case when foo.high > foo2.high then foo2.high else foo.high end from (SELECT day, high from alldata_ia where station = 'IA2203') as foo, (SELECT day + '1 day'::interval as day2, sday, high from alldata_ia where station = 'IA2203') as foo2 WHERE foo.day = foo2.day2 ) as f GROUP by high ORDER by high DESC")

threshold = []
doy = []
for row in ccursor:
  if len(threshold) > 0 and row[0] + 1 != threshold[-1]:
    threshold.append( row[0] + 1)
    doy.append( doy[-1])
  threshold.append( row[0] )
  ts = mx.DateTime.strptime("2000"+row[1], '%Y%m%d')
  jday = int(ts.strftime("%j"))
  if len(doy) > 0 and jday < doy[-1]:
    jday = doy[-1]
  doy.append( jday )

import matplotlib.pyplot as plt
import numpy

(fig, ax) = plt.subplots(1,1)

ax.barh( numpy.array(threshold)-0.4, doy, fc='pink', ec='pink')
ax.set_ylim(60,120)
ax.grid(True)
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlim(min(doy),366)
ax.set_title("Des Moines 1880-2012 Latest Date for\nTwo Days Above High Temperature") 
ax.text(242, 96, 'x', color='r', fontsize=15, va='center', ha='center')
ax.set_ylabel("High Temperature $^{\circ}\mathrm{F}$")
ax.set_xlabel("Red X is 29-30 August 2012 at 96$^{\circ}\mathrm{F}$")

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
