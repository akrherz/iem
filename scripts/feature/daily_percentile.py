import iemdb
import mx.DateTime
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

percentile = []
sts = mx.DateTime.DateTime(2011,12,1)
ets = mx.DateTime.DateTime(2012,2,15)
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
  SELECT extract(year from day + '1 month'::interval) as yr, 
  avg((high+low)/2.) from alldata_ia where station = 'IA0200'
  and month in (12,1,2) and day > '1893-11-30'
  and extract(doy from  day + '1 month'::interval) < %s 
  GROUP by yr ORDER by avg ASC
  """ % (i,))
  cnt = 0
  for row in ccursor:
    cnt += 1
    if row[0] == 2012:
      break
  print now, cnt, float(cnt) / 119.0 * 100.0
  #percentile.append( float(cnt) / 119.0 * 100.0 )
  percentile.append( 119.0 - float(cnt) )
  i += 1
  now += interval

import matplotlib.pyplot as plt
import numpy as np
fig = plt.figure()
ax = fig.add_subplot(111)

bars = ax.bar( np.arange(1,len(percentile)+1) -0.4, percentile )
ax.text(len(percentile), percentile[-1]+2, int(percentile[-1]))
#bars[-3].set_facecolor('r')
#bars[-2].set_facecolor('r')
#bars[-1].set_facecolor('r')
ax.set_xlim(0.5,len(percentile)+2)
ax.set_ylim(0,100)
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)
ax.set_ylabel("Rank [1 = warmest]")
#ax.set_xlabel("D, last three days forecasted")
ax.set_title("Ames Avg Temp [high+low] 1 Dec - 14 Feb Rank\n2011-2012 against years 1893-2011")
ax.set_yticks( (0,25,50,75,100) )
ax.grid(True)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
