import iemdb
import numpy
import mx.DateTime
import copy
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

climate = {}
ccursor.execute("""SELECT avg(high), stddev(high), sday,
  avg(low), stddev(low) from alldata_ia
  where station = 'IA2203' and year between 1971 and 2001 GROUP by sday""")
#ccursor.execute("""SELECT high, to_char(valid, 'mmdd') from climate
#  where station = 'IA2203' """)
for row in ccursor:
  climate[row[2]] = {'stddev': 0, 'avg': row[0],
       'lstddev': 0, 'lavg': row[3]}

ccursor.execute("""SELECT day, sday, high, low from alldata_ia 
  where station = 'IA2203' and day >= '2012-03-01' ORDER by day ASC""")

maxRunning = 0
running = 0
vals = []
lvals = []
for row in ccursor:
  if float(row[2] - climate[row[1]]['avg']) >= 10.0:
    running += 1
  else:
    if running > 10:
      print row, running
    if running > maxRunning:
      maxRunning = running
      print 'Max', row, running
    running = 0
  vals.append( float(row[2] - climate[row[1]]['avg']) )
  lvals.append( float(row[3] - climate[row[1]]['lavg']) )

sts = mx.DateTime.DateTime(2012,3,1)
ets = mx.DateTime.DateTime(2012,4,5)
interval = mx.DateTime.RelativeDateTime(days=1)
now = sts
xticks = []
xticklabels = []
i = 0
while now < ets:
  fmt = "%-d"
  if now.day == 1:
    fmt = "%-d\n%b"
  if now.day == 1 or now.day % 7 == 0:
    xticks.append( i )
    xticklabels.append( now.strftime(fmt))
  i += 1
  now += interval

import matplotlib.pyplot as plt
fig = plt.figure()

ax = fig.add_subplot(211)
bars = ax.bar(numpy.arange(0, len(vals))-0.4, vals, fc='b')
for i in range(len(vals)):
  if vals[i] > 0:
    bars[i].set_facecolor('r')
ax.set_xticks( xticks )
ax.set_xticklabels( xticklabels )
ax.grid(True)
ax.set_xlim(-0.5,36)
ax.set_ylim(-20,40)
ax.set_ylabel("High Temp Departure $^{\circ}\mathrm{F}$")
ax.set_title("1 March - 4 April 2012: Des Moines Daily Departures")
ax.text(9,-9, "26 Straight Days 10+$^{\circ}\mathrm{F}$ over average")
ax.plot([8.5,34.5], [10,10], color='k')

ax2 = fig.add_subplot(212)
bars = ax2.bar(numpy.arange(0, len(vals))-0.4, lvals, fc='b')
for i in range(len(vals)):
  if lvals[i] > 0:
    bars[i].set_facecolor('r')
ax2.set_xticks( xticks )
ax2.set_xticklabels( xticklabels )
ax2.grid(True)
ax2.set_xlim(-0.5,36)
ax2.set_ylim(-20,40)
ax2.set_ylabel("Low Temp Departure $^{\circ}\mathrm{F}$")


fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
