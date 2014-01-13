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

yearlymax = [0]*(2015-1934)
maxvalid = [0]*(2015-1934)
acursor.execute("""
  SELECT valid, tmpf from alldata where station = 'CID' and tmpf > -40 
  and tmpf < 30
  and valid > '1930-01-01' ORDER by valid ASC
""")
running = False
last = None
lmax = 0
for row in acursor:
    ts = mx.DateTime.strptime(row[0].strftime("%Y%m%d%H%M"), "%Y%m%d%H%M")
    # Case 1: Noop
    if not running and row[1] >= 0:
        continue
    # Case 2: streak continues
    if running and row[1] < 0:
        continue
    # Case 3: Starting a new streak
    if not running and row[1] < 0:
        last = ts
        running = True
        continue
    # Case 4: Ending a streak
    if running and row[1] >= 0:
        diff = (ts - last).hours
        if diff > lmax:
            lmax = diff
            print row, last, diff
        running = False

import matplotlib.pyplot as plt
import numpy
yearlymax = numpy.array( yearlymax )
maxvalid = numpy.array( maxvalid )
fig = plt.figure()
ax = fig.add_subplot(111)
bars = ax.bar(numpy.arange(1933,2014)-0.4, yearlymax )
for bar in bars:
    if bar.get_height() <= bars[-1].get_height():
        bar.set_facecolor('r')
        bar.set_edgecolor('r')

ax.set_xlim(1935,2014)
ax.grid(True)
ax.set_ylabel("Consec Hours")
ax.set_title("Des Moines Max Consecutive Hours Below Freezing\nPeriod within November [1936-2013]")
ax.set_xlabel("*blue bars are periods longer than 2013")
"""
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
"""
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
