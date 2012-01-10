import iemdb 
import numpy as np
import datetime
import mx.DateTime
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
 select foo2.sday, foo2.min, (foo2.min - foo3.avg) / foo3.stddev from 
 (select sday, avg(high), stddev(high) from alldata_ia where 
  station = 'IA0200' GROUP by sday) as foo3 JOIN (select sday, min(high) 
  from (select sday, high, rank() OVER 
  (partition by sday order by high DESC) from alldata_ia 
  where station = 'IA0200') as foo where rank < 6 GROUP by sday) as foo2 
  on (foo2.sday = foo3.sday)
""")

p95 = np.zeros( (366,) , 'f')
pdev = np.zeros( (366,) , 'f')
for row in ccursor:
  ts = mx.DateTime.strptime("2000%s" % (row[0],), '%Y%m%d')
  doy = int((ts - mx.DateTime.DateTime(2000,1,1)).days)
  p95[ doy ] = row[1]
  pdev[ doy ] = row[2]


import matplotlib.pyplot as plt
import mx.DateTime
fig = plt.figure()
ax = fig.add_subplot(211)

ax.bar(np.arange(0,366) - 0.5, p95, ec='tan', fc='tan')

ax.grid(True)
ax.set_ylabel("High Temperature $^{\circ}\mathrm{F}$")
ax.set_title("Ames 95th Percentile High Temperature [1893-2011]")
ax.set_xlim(-0.4,366)
ax.set_ylim(0,100)
xticks = []
xticklabels = []
for i in range(0,366):
  ts = mx.DateTime.DateTime(2000,1,1) + mx.DateTime.RelativeDateTime(days=i)
  if ts.day == 1:
    xticks.append(i)
    xticklabels.append( ts.strftime("%b") )
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)

ax.annotate("50s in December are like\n100 degrees in July", xy=(340, 50),  
  xycoords='data',
                xytext=(-210, -40), textcoords='offset points',
                bbox=dict(boxstyle="round", fc="0.8"),
                arrowprops=dict(arrowstyle="->",
                connectionstyle="angle3,angleA=-90,angleB=0"))

ax.annotate("", xy=(200, 90),
  xycoords='data',
                xytext=(0, -80), textcoords='offset points',
                bbox=dict(boxstyle="round", fc="0.8"),
                arrowprops=dict(arrowstyle="->",
                connectionstyle="angle3,angleA=-90,angleB=0"))


ax2 = fig.add_subplot(212)
ax2.bar( np.arange(0,366) - 0.5, pdev, ec='skyblue', fc='skyblue')
ax2.set_xlim(-0.4,366)
ax2.set_xticks(xticks)
ax2.set_xticklabels(xticklabels)
ax2.set_xlim(-0.4,366)
ax2.set_ylabel("Departure from Average [$\sigma$]")
ax2.grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
