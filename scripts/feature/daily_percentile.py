import iemdb
import mx.DateTime
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

percentile = []
departure = []
sts = mx.DateTime.DateTime(2012,1,1)
ets = mx.DateTime.DateTime(2012,7,1)
interval = mx.DateTime.RelativeDateTime(days=1)
now = sts
i = 2
xticks = []
xticklabels = []
while now < ets:
  if now.day == 1:
    xticks.append( i-1 )
    xticklabels.append( now.strftime("%-d\n%B"))
  if now.day in (7,14,21,28):
    xticks.append( i-1 )
    xticklabels.append( now.strftime("%-d"))

  ccursor.execute("""
  SELECT year, 
  avg((high+low)/2.) from alldata_ia where station = 'IA2203'
  and month in (1,2,3,4,5,6) and day > '1893-11-30'
  and sday <= '%s' 
  GROUP by year ORDER by avg DESC
  """ % (now.strftime("%m%d"),))
  d2012 = -99
  rank = 1
  best = None
  for row in ccursor:
    if best is None:
      best = row[1]
    if row[0] == 2012:
      break
    rank += 1
  if best == row[1]:
    row2 = ccursor.fetchone()
    best = row2[1]
  departure.append( float(row[1] - best) )
  print now, rank, float(rank) / 119.0 * 100.0, row[1] - best
  #percentile.append( float(cnt) / 119.0 * 100.0 )
  percentile.append( rank )
  i += 1
  now += interval

import matplotlib.pyplot as plt
import numpy as np
fig = plt.figure()
ax = fig.add_subplot(211)

bars = ax.bar( np.arange(1,len(percentile)+1) -0.4, percentile, fc='b', ec='b' )
#for i in range(-4,0):
#  bars[i].set_facecolor('g')
ax.text(len(percentile), percentile[-1]+2, int(percentile[-1]))
#bars[-3].set_facecolor('r')
#bars[-2].set_facecolor('r')
#bars[-1].set_facecolor('r')
ax.set_xlim(0.5,len(percentile)+2)
ax.set_ylim(0,120)
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)
ax.set_ylabel("Rank [1 = warmest]")
#ax.set_xlabel("D, last three days forecasted")
ax.set_title("Ames Avg Temp [high+low] 2012 vs [1893-2011]")
ax.grid(True)

ax2 = fig.add_subplot(212)
bars = ax2.bar( np.arange(1,len(percentile)+1) -0.4, departure , fc='b', ec='b')
for i in range(-120,0):
    if departure[i] > 0:
        bars[i].set_facecolor('r')
        bars[i].set_edgecolor('r')
#for i in range(-4,0):
#  bars[i].set_facecolor('g')
ax2.set_xlim(0.5,len(percentile)+2)
ax2.set_xticks(xticks)
ax2.set_ylabel("Difference from warmest $^{\circ}\mathrm{F}$")
ax2.set_xticklabels(xticklabels)
ax2.grid(True)
#ax2.set_xlabel("thru 1 Jul")

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
