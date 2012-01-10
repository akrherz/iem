import iemdb
import numpy
import ephem
import mx.DateTime
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
ISUAG = iemdb.connect('isuag', bypass=True)
icursor = ISUAG.cursor()

def compute_daytime():
    arr = []
    sun = ephem.Sun()
    ames = ephem.Observer()
    ames.lat = '41.99206'
    ames.long = '-93.62183'
    sts = mx.DateTime.DateTime(2000,1,1)
    ets = mx.DateTime.DateTime(2001,1,1)
    interval = mx.DateTime.RelativeDateTime(days=1)
    now = sts
    while now < ets:
        ames.date = now.strftime("%Y/%m/%d")
        rise = mx.DateTime.strptime(str(ames.next_rising(sun)), "%Y/%m/%d %H:%M:%S")
        set = mx.DateTime.strptime(str(ames.next_setting(sun)), "%Y/%m/%d %H:%M:%S")
        if set < rise:
            ames.date = (now - interval).strftime("%Y/%m/%d")
            rise = mx.DateTime.strptime(str(ames.next_rising(sun)), "%Y/%m/%d %H:%M:%S")
        arr.append( (set-rise).minutes / 60.0)
        now += interval

    return arr

def smooth(x,window_len=11,window='hanning'):

    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"


    s=numpy.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=numpy.ones(window_len,'d')
    else:
        w=eval('numpy.'+window+'(window_len)')

    y=numpy.convolve(w/w.sum(),s,mode='valid')
    return y

daylight = compute_daytime()

icursor.execute("""
select extract(doy from valid) as doy, avg(c30) from daily where station = 'A130209' GROUP by doy ORDER by doy ASC
""")
soil = []
for row in icursor:
    soil.append( row[1] )

ccursor.execute("""
SELECT high, low from climate where station = 'IA0200' ORDER by valid ASC
""")
highs = []
lows = []
for row in ccursor:
    highs.append( row[0] )
    lows.append( row[1] )

import matplotlib.pyplot as plt
import numpy as np
fig = plt.figure()
ax = fig.add_subplot(111)

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

print len(highs), len(lows)
ax.plot( np.arange(1,367), highs, color='r', label='High Temp')
ax.plot( np.arange(1,367), lows, color='b', label='Low Temp')
ax.plot( np.arange(1,367), soil, color='g', label='4in Soil')
ax2 = ax.twinx()
ax2.plot( np.arange(1,367), daylight, color='k')
ax.set_xticks(xticks)
ax.set_xlim(min(xticks)-1, max(xticks)+32)
ax2.set_xticklabels(xticklabels)
ax.set_ylabel("Temperature $^{\circ}\mathrm{F}$")
ax2.set_ylabel("Daylight Length [hours]")
#ax.set_xlabel("1 Jan - 26 May 2011")
ax.set_title("Ames Daily Climatologies")
ax.grid(True)
ax.legend(loc=2)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
