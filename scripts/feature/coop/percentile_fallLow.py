# Month percentile 

import sys, os, random
sys.path.append("../lib/")
import iemplot
import numpy

import mx.DateTime
now = mx.DateTime.now()

import network
nt = network.Table("IACLIMATE")
import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

cum = numpy.zeros( (int(2012-1893),91), 'f')

ccursor.execute("""SELECT day, precip from alldata_ia
     WHERE station = 'IA2203' and year > 1892 and month in (9,10,11)
     ORDER by day ASC""")
running = 0
year = 1892
for row in ccursor:
  if row[0].year != year:
    running = 0
    sep1 = mx.DateTime.DateTime(row[0].year, 9, 1)
  year = row[0].year
  running += row[1]
  day = mx.DateTime.DateTime(row[0].year, row[0].month, row[0].day)
  cum[year-1893, int((day-sep1).days)] = running

ets = mx.DateTime.DateTime(2011,12,1)
interval = mx.DateTime.RelativeDateTime(days=1)
end11 = int((day-sep1).days) + 2
while day < ets:
  cum[2011-1893,int((day-sep1).days)] = running
  day += interval

ranks = []
for day in range(0,91):
  d2011 = cum[-1,day]
  vals = cum[:-1,day].copy()
  vals.sort()
  r = 0
  for val in vals:
    if d2011 < val:
       break
    r += 1
  ranks.append( r )

ranks14 = []
for day in range(0,91):
  d14 = cum[int(1914-1893),day]
  vals = cum[:,day].copy()
  vals.sort()
  r = 0
  for val in vals:
    if d14 <= val:
       break
    r += 1
  ranks14.append( r )


xticks = []
xticklabels = []
ranks66 = []
for day in range(0,91):
  d66 = cum[int(1966-1893),day]
  vals = cum[:,day].copy()
  vals.sort()
  r = 0
  for val in vals:
    if d66 <= val:
       break
    r += 1
  ranks66.append( r )
  ts = sep1 + mx.DateTime.RelativeDateTime(days=day)
  if ts.day in [1,8,15,22,29]:
    fmt = "%-d"
    if ts.day == 1:
       fmt = "%-d\n%b"
    xticks.append( day )
    xticklabels.append( ts.strftime(fmt) )
    


import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111)

ax.plot( numpy.arange(0,end11), numpy.array(ranks[:end11]) +1,  color='b', label='2011 1.94" (12$^{th}$)' )
ax.plot( numpy.arange(end11,91), numpy.array(ranks[end11:]) +1, '.', color='b', label='Rest 2011 Dry' )
ax.plot( numpy.arange(0,91), numpy.array(ranks66) +1, color='r' , label='1966 1.74"')
ax.plot( numpy.arange(0,91), numpy.array(ranks14) +1, color='g' , label='1914 20.21"')
ax.set_xticks( xticks )
ax.set_xticklabels( xticklabels )
ax.set_ylim(0,120)
ax.set_ylabel("Rank [1 driest, 119 wettest]")
ax.set_title("Des Moines Fall (Sep,Oct,Nov) Precipitation [1893-2011]\n* 2011 Data thru 27 Oct")
ax.set_xlabel("Rank to date from 1 September")
ax.grid(True)
ax.legend(loc=(.5,.5))

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
