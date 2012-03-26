import iemdb
import numpy
import ephem
import mx.DateTime

def compute_sunrise(lat, long):
    arr = []
    sun = ephem.Sun()
    ames = ephem.Observer()
    ames.lat = lat
    ames.long = long
    sts = mx.DateTime.DateTime(2012,1,1)
    ets = mx.DateTime.DateTime(2013,1,1)
    interval = mx.DateTime.RelativeDateTime(days=1)
    now = sts
    doy = []
    i = 1
    returnD = 0
    findT = 0
    while now < ets:
        ames.date = now.strftime("%Y/%m/%d")
        rise = mx.DateTime.strptime(str(ames.next_rising(sun)), "%Y/%m/%d %H:%M:%S")
        rise = rise.localtime()
        set = mx.DateTime.strptime(str(ames.next_setting(sun)), "%Y/%m/%d %H:%M:%S")
        #if set < rise:
        #    ames.date = (now - interval).strftime("%Y/%m/%d")
        #    rise = mx.DateTime.strptime(str(ames.next_rising(sun)), "%Y/%m/%d %H:%M:%S")
        #arr.append( (set-rise).minutes / 60.0)
        offset = rise.hour * 60 + rise.minute
        if now.month == 3 and now.day == 11:
            findT = arr[-1]
            arr.append(None)
            doy.append( i + 0.5)
        if now.month == 11 and now.day == 4:
            arr.append(None)
            doy.append( i + 0.5)
        if returnD == 0 and offset <= findT:
            returnD = i
        arr.append( offset )
        doy.append( i )
        i += 1
        now += interval

    return doy, arr, returnD

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

doy, ames, rames = compute_sunrise('41.99206','-93.62183')
doy, stl, rstl = compute_sunrise('38.75245','-90.3734')
doy, msp, rmsp = compute_sunrise('44.88537','-93.23131')

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=12)
fig = plt.figure()
ax = fig.add_subplot(111)

xticks = []
xticklabels = []
sts = mx.DateTime.DateTime(2012,1,1)
ets = mx.DateTime.DateTime(2013,1,1)
interval = mx.DateTime.RelativeDateTime(months=1)
now = sts
while now < ets:
  xticks.append( (now - mx.DateTime.DateTime(2012,1,1)).days )
  xticklabels.append( now.strftime("%b") )
  now += interval

#print len(highs), len(lows)
ax.plot( doy, ames, color='k', label="Ames - %s days" % (rames - 71,))
print [71, rames], [ames[69], ames[rames]]
ax.plot( [71, rames], [ames[69], ames[rames]], color='k', linestyle='--')
ax.plot( doy, msp, color='b', label="Minneapolis - %s days" % (rmsp-71,))
ax.plot( [71, rmsp], [msp[69], msp[rmsp]], color='b', linestyle='--')
ax.plot( doy, stl, color='r', label='Saint Louis - %s days' % (rstl-71,))
ax.plot( [71, rstl], [stl[69], stl[rstl]], color='r', linestyle='--')
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)
ax.set_xlim(min(xticks)-1, max(xticks)+32)
ax.set_ylabel("Local Sunrise Time (CST or CDT)")
ax.set_yticks(numpy.arange(300,510,30))
ax.set_yticklabels( ('5 AM', '5:30', '6 AM', '6:30', '7 AM', '7:30', '8 AM', '8:30'))
#ax.set_xlabel("1 Jan - 26 May 2011")
ax.set_title("Number of Days to retrieve our stolen morning daylight hour")
ax.grid(True)
ax.legend(loc=4, prop=prop)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
