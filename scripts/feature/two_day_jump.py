#!/mesonet/python/bin/python
import mx.DateTime
from pyIEM import iemdb
i = iemdb.iemdb()
coop = i['coop']

jumpup = [0]*366
jumpdown = [0]*366
jumpup30 = [0]*12
jumpdown30 = [0]*12

rs = coop.query("SELECT day, high from alldata WHERe stationid = 'ia0200' and year < 2010 ORDER by day ASC").dictresult()
roller = [rs[0]['high']]*3
m = 0
for row in rs:
  tz = mx.DateTime.strptime(row['day'], '%Y-%m-%d')
  h = row['high']
  roller.pop()
  roller.insert(0, h)
  jump = h - roller[1]
  j = int(tz.strftime("%j")) - 1
  if jump < jumpdown[j]:
    jumpdown[j] = jump
  if jump > jumpup[j]:
    jumpup[j] = jump
  if jump <= -30:
    jumpdown30[ tz.month - 1] += 1
  if jump >= 30:
    jumpup30[ tz.month - 1] += 1

import matplotlib.pyplot as plt
import numpy
import iemplot

fig = plt.figure()
ax = fig.add_subplot(211)

ax.scatter( numpy.arange(0, 366), jumpup, color='r', marker='+', label="Rise")
ax.scatter( numpy.arange(0, 366), 0 - numpy.array(jumpdown), color='b', marker='+', label="Drop")
ax.legend(ncol=2,loc=9)
ax.set_xlim(0,366)
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.grid(True)
ax.set_title("Ames [1893-2009] One Day High Temperature Change")
ax.set_ylabel("Maximum Change $^{\circ}\mathrm{F}$")

ax = fig.add_subplot(212)
ax.bar( numpy.arange(0, 12) - 0.33, jumpup30, width=0.33, color='r', label='Rise')
ax.bar( numpy.arange(0, 12), jumpdown30, width=0.33, color='b', label='Drop')
ax.legend(ncol=2, loc=9)
ax.set_ylabel("Occurences of 30+ Drop or Rise")
ax.set_xticks( numpy.arange(0,12) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlim(-0.33,11.66)
ax.grid(True)
ax.set_ylim(0,30)

fig.savefig("test.ps")
#iemplot.makefeature("test")
