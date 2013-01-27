import iemdb, numpy
import datetime
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""select o.station, o.day, o.high, c.high, o.low, c.low from 
  alldata_ia o JOIN climate c ON 
  (c.station = o.station and to_char(c.valid, 'mmdd') = o.sday) 
  and o.station = 'IA0200' and o.day >= '2012-12-01' ORDER by day ASC""")

days = []
days2 = []
ohighs = []
olows = []
chighs = []
clows = []
for row in ccursor:
    days.append( datetime.datetime(row[1].year, row[1].month, row[1].day, 0) - datetime.timedelta(hours=6) )
    days2.append( datetime.datetime(row[1].year, row[1].month, row[1].day, 0) )
    ohighs.append( row[2] )
    chighs.append( row[3] )
    olows.append( row[4] )
    clows.append( row[5] )

import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects

(fig, ax) = plt.subplots(1, 1)

ax.bar(days, ohighs, width=0.25, fc='r', ec='r', label="High")
ax.bar(days2, olows, width=0.25, fc='b', ec='b', label="Low")

ax.plot(days, chighs, linewidth=4, zorder=2, color='k')
ax.plot(days, chighs, linewidth=2, zorder=2, color='r')
ax.plot(days, clows, linewidth=4, zorder=2, color='k')
ax.plot(days, clows, linewidth=2, zorder=2, color='b')
ax.set_xlim(datetime.datetime(2012,11,29,23),datetime.datetime(2013,1,7))
#ax.set_ylim(50,85)
ax.annotate("19-20 Dec Snowstorm", xy=(datetime.datetime(2012,12,20), 35), xycoords='data',
                xytext=(10, 50), textcoords='offset points',
                bbox=dict(boxstyle="round", fc="0.8"),
                arrowprops=dict(arrowstyle="->",
                connectionstyle="angle3,angleA=0,angleB=-90"))
 
ax.grid(True)
ax.set_title("1 Dec 2012 - 7 Jan 2013 : Ames Daily Temperatures")
#ax.set_xlabel("16-20 Forecasted")
ax.set_ylabel("Temperature $^{\circ}\mathrm{F}$")
ax.legend()
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
