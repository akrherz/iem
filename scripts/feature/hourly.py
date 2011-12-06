
from matplotlib import pyplot as plt
import iemdb
import mx.DateTime
asos = iemdb.connect('asos', bypass=True)
acursor = asos.cursor()

acursor.execute("""
select doy, avg(case when hr in (14,15,16,17,19,20,21) then avg else null end) as cdt, 
 avg(case when hr in (15,16,17,18,19,20,21,22) then avg else null end) as cst from 
  (select extract(doy from valid) as doy, 
   extract(hour from (valid at time zone 'UTC')+'10 minutes'::interval) as hr, avg(tmpf) from alldata where station = 'DSM' and tmpf > -50 GROUP by doy, hr) as foo GROUP by doy ORDER by doy ASC
""")

work = []

for row in acursor:
    work.append( float(row[2]) - float(row[1]))
    

acursor.execute("""
select doy, avg(case when hr in (4,5,6,7,8,9,10,11) then avg else null end) as cdt, 
 avg(case when hr in (5,6,7,8,9,10,11,12) then avg else null end) as cst from 
  (select extract(doy from valid) as doy, 
   extract(hour from (valid at time zone 'UTC')+'10 minutes'::interval) as hr, avg(tmpf) from alldata where station = 'DSM' and tmpf > -50 GROUP by doy, hr) as foo GROUP by doy ORDER by doy ASC
""")

sleep = []

for row in acursor:
    sleep.append( float(row[2]) - float(row[1]))

    
import numpy

fig = plt.figure()
ax = fig.add_subplot(111)

ax.set_title("Des Moines [1933-2011] Air Temperature Change with CDT from CST\nWork Day: 8 AM - 4 PM, Sleep: 10 PM - 6 AM ")
ax.plot( numpy.arange(1,366), work[:-1], 'r', label="Work Day")
ax.plot( numpy.arange(1,366), sleep[:-1], 'b', label="Sleepy Time")
ax.set_xlim(0,366)
ax.set_ylim(-3,3)
xticks = []
xticklabels = []
sts = mx.DateTime.DateTime(2000,1,1)
ets = mx.DateTime.DateTime(2001,1,1)
interval = mx.DateTime.RelativeDateTime(months=1)
now = sts
while now < ets:
  xticks.append( (now - mx.DateTime.DateTime(2000,1,1)).days )
  xticklabels.append( now.strftime("%b") )
  now += interval
ax.fill([90,90,306,306], [0.5,2.5,2.5,0.5], facecolor='none', edgecolor='k')
ax.text(205,0.85, 'Summer\nCDT Workday is cooler,\nlower air conditioning cost', ha='center', va='center')

ax.text(60,0.3, 'Winter\nCST Workday is warmer,\nlower heating cost', ha='center', va='center')


ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)
ax.grid()
ax.legend(ncol=2,loc=3)
ax.set_ylabel("Temperature Difference (CST-CDT) $^{\circ}\mathrm{F}$")
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
