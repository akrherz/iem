import iemdb
import mx.DateTime
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

def getyear(ts):
    if ts.month in (1,2,3,4,5,6):
        return ts.year
    return ts.year + 1
def normalize(ts):
    if ts.month in (1,2,3,4,5,6):
        return mx.DateTime.DateTime(2010,ts.month,ts.day)
    return mx.DateTime.DateTime(2009,ts.month, ts.day)

yearlymax = [0]*(2013-1934)
maxvalid = [0]*(2013-1934)
acursor.execute("""
  SELECT valid, tmpf from alldata where station = 'DSM' and tmpf < 40 
  and valid > '1933-06-01' ORDER by valid ASC
""")
running = False
last = None
for row in acursor:
    ts = mx.DateTime.strptime(row[0].strftime("%Y%m%d%H%M"), "%Y%m%d%H%M")
    if running and row[1] < 32:
        continue
    if not running and row[1] < 32:
        last = ts
        running = True
        continue
    if running and row[1] >= 32:
        diff = (ts - last).hours
        lmax = yearlymax[getyear(ts)-1934]
        if diff > lmax:
            print 'New', diff, getyear(ts)
            yearlymax[getyear(ts)-1934] = diff
            maxvalid[getyear(ts)-1934] = float(normalize(last))
        running = False

import matplotlib.pyplot as plt
import numpy
yearlymax = numpy.array( yearlymax )
maxvalid = numpy.array( maxvalid )
fig = plt.figure()
ax = fig.add_subplot(211)
bars = ax.bar(numpy.arange(1934,2013)-0.4, yearlymax / 24.0)
for bar in bars:
  if bar.get_height() <= bars[-1].get_height():
    bar.set_facecolor('r')
    bar.set_edgecolor('r')

ax.set_xlim(1933,2013)
ax.grid(True)
ax.set_ylabel("Consec Hours [days]")
ax.set_title("Des Moines Yearly Max Consecutive Hours Below Freezing [1934-2012]")
ax.set_xlabel("*2012 thru 1 Feb, red bars less <= 2012")

sts = mx.DateTime.DateTime(2009,11,1)
ets = mx.DateTime.DateTime(2010,5,1)
interval = mx.DateTime.RelativeDateTime(months=1)
now = sts
xticks = []
xticklabels = []
while now < ets:
    xticks.append( float(now) )
    xticklabels.append( now.strftime("%-d\n%b") )
    now += interval 
ax2 = fig.add_subplot(212)
bars = ax2.barh( numpy.arange(1934,2013), yearlymax*60*60, left=maxvalid)
for bar in bars:
  if bar.get_width() <= bars[-1].get_width():
    bar.set_facecolor('r')
    bar.set_edgecolor('r')
ax2.set_xticks( xticks )
ax2.set_ylabel("When Streak Occurred")
ax2.set_xticklabels( xticklabels )
ax2.grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
