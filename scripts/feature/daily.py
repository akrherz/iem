import iemdb
import numpy
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

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


acursor.execute("""
--- select doy, count(*), sum(case when t >=80 then 1 else 0 end), 
--- sum(case when t >= 80 and d < 60 then 1 else 0 end) from 
--- (select extract(year from valid) as year, extract(doy from valid) as doy, max(tmpf) as t, 
--- max(dwpf) as d from alldata where station = 'DSM' and extract(hour from valid) 
--- between 11 and 19 GROUP by year, doy) as foo GROUP by doy ORDER by doy
 SELECT doy, sum(case when data > 2 then 1 else 0 end),
 sum(case when data > 0 then 1 else 0 end), count(*) from
 (SELECT extract(year from valid) as yr, extract(doy from valid) as doy, 
 sum(case when sknt > 26 or gust > 26 then 1 else 0 end) as data
 from alldata where station = 'DSM' and sknt >= 0 
 and extract(minute from valid) in (50,51,52,53,54,55,56,57,58,59,0) GROUP by yr, doy) as foo
 GROUP by doy ORDER by doy ASC
""")

import datetime
data3 = numpy.zeros( (366,), 'f')
data1 = numpy.zeros( (366,), 'f')
for row in acursor:
    data3[int(row[0])-1] = float(row[1]) / float(row[3]) * 100.0
    data1[int(row[0])-1] = float(row[2]) / float(row[3]) * 100.0

import mx.DateTime
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

smdata3 = smooth(data3, window='flat')
smdata1 = smooth(data1, window='flat')
print numpy.shape(smdata3)
ax.plot( np.arange(1,len(smdata3)+1) - 0.3, smdata3, color='r', label='3+ Hours / Day')
ax.plot( np.arange(1,len(smdata1)+1) - 0.3, smdata1, color='b', label='1+ Hours / Day')
ax.set_ylim(0,35)
ax.set_xticks(xticks)
ax.set_xlim(min(xticks)-1, max(xticks)+1)
ax.set_xticklabels(xticklabels)
ax.set_xlim(0., len(data3)+1)
ax.set_xlabel("* Data has a two week smoothing applied")
ax.set_ylabel("Frequency [%]")
#ax.set_xlabel("1 Jan - 26 May 2011")
ax.set_title("Des Moines Frequency of Wind Obs Over 30mph [1933-2011]")
ax.grid(True)
ax.legend()
"""
sts = mx.DateTime.DateTime(2011,1,1)
j = 0
ax.text(10,175, 'Days over 100', size=16)
for i in range(len(data)):
    if data[i] >= 100:
        ets = sts + mx.DateTime.RelativeDateTime(days=i)
        txt = "%s. %s - %s" % (j+1, ets.strftime("%b %d"), data[i])
        ax.text(10, 150-(j*24), txt, size=16)
        j += 1
"""
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
