import iemdb
import numpy
import math
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

acursor.execute("""
   select to_char(valid, 'YYMMDDHH24'), dwpf from alldata where station = 'DSM' 
   and dwpf >= 50
""")

obs = {}
for row in acursor:
    obs[ row[0] ] = row[1]

import mx.DateTime

sts = mx.DateTime.DateTime(1933,1,1)
ets = mx.DateTime.DateTime(2011,8,10)
interval = mx.DateTime.RelativeDateTime(hours=1)

now = sts
mrun = numpy.zeros((2012-1933))
mday = numpy.zeros((2012-1933))
mcnt = numpy.zeros((2012-1933))
mend = [0]*(2012-1933)
missing = 0
running = 0
while now < ets:
    if not obs.has_key( now.strftime("%y%m%d%H")):
        missing += 1
        if missing > 6:
            if running > mrun[ now.year - 1933 ]:
                mrun[ now.year - 1933 ] = running
                mday[ now.year - 1933 ] = int(now.strftime("%j"))
                mend[ now.year - 1933 ] = now
            running = 0
        if running > 0:
            running += 1
        now += interval
        continue
    missing = 0
    dwpf = obs[  now.strftime("%y%m%d%H") ]
    if dwpf >= 68:
        running += 1
        mcnt[ now.year - 1933 ] += 1
    else:
        running = 0
    if running > mrun[ now.year - 1933 ]:
        mrun[ now.year - 1933 ] = running
        mday[ now.year - 1933 ] = int(now.strftime("%j"))
        mend[ now.year - 1933 ] = now
    now += interval

for yr in range(1933,2012):
    print yr, mrun[yr-1933], mday[yr-1933], mcnt[yr-1933], mend[yr-1933], mend[yr-1933] - mx.DateTime.RelativeDateTime(hours=mrun[yr-1933])

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(211)
ax.set_title("Des Moines Dew Points (1933-2011)\nMaximum Consec. Hours at or above 68$^{\circ}\mathrm{F}$")
ax.set_ylabel("Days")
ax.grid(True)
ax.set_xlim(1932.5,2011.5)
bar = ax.bar(numpy.arange(1933,2012)-0.4, mrun / 24.0)
bar[-1].set_facecolor('r')
#bar[-1].set_edgecolor('r')

ax2 = fig.add_subplot(212)
ax2.set_title("Day Period over which longest streak occured")
ax2.set_ylabel("Year")
#ax2.set_xlabel("*2011 data through 7 August, streak still going")
ax2.grid(True)
ax2.set_ylim(2012,1932.5)
bars = ax2.barh( numpy.arange(1933,2012) - 0.4, (mrun/24.0), left=(mday-(mrun/24.0)), ec='b', fc='b')
bars[-1].set_facecolor('r')
bars[-1].set_edgecolor('r')
ax2.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax2.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax2.set_xlim(numpy.min((mday-(mrun/24.0))) - 5, numpy.max(mday) + 5)

"""
ax2 = fig.add_subplot(212)
ax2.set_title("Total Hours at or above 60$^{\circ}\mathrm{F}$")
ax2.set_ylabel("Hours")
ax2.set_xlabel("*2011 data through 7 August")
ax2.grid(True)
ax2.set_xlim(1932.5,2011.5)
bar2 = ax2.bar(numpy.arange(1933,2012)-0.4, mcnt)
bar2[-1].set_facecolor('r')
#bar2[-1].set_edgecolor('r')
"""
fig.savefig('test.png')
#import iemplot
#iemplot.makefeature('test')
