import psycopg2
import numpy as np

def smooth(x,window_len=11,window='hanning'):

    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"


    s=np.r_[2*x[0]-x[window_len:1:-1],x,2*x[-1]-x[-1:-window_len:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=np.ones(window_len,'d')
    else:
        w=eval('np.'+window+'(window_len)')

    y=np.convolve(w/w.sum(),s,mode='same')
    return y[window_len-1:-window_len+1]


ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
cursor = ASOS.cursor()

cursor.execute("""
 SELECT doy, count(*),
 sum(case when wind >= 10 then 1 else 0 end),
 sum(case when wind >= 10 and (tmpf - 5.0) > avg then 1 else 0 end),
 sum(case when (tmpf - 5.0) > avg then 1 else 0 end),
 sum(case when wind >= 10 and (tmpf + 5.0) < avg then 1 else 0 end),
 sum(case when (tmpf + 5.0) < avg then 1 else 0 end) from
 (SELECT extract(doy from valid) as doy, tmpf, sknt * 1.15 as wind,
 avg(tmpf) over (partition by extract(doy from valid)) from alldata WHERE station = 'DSM'
 and extract(hour from valid + '10 minutes'::interval) = 15 and 
 extract(minute from valid + '10 minutes'::interval) <= 10 and
 tmpf is not null) as foo
 GROUP by doy ORDER by doy ASC
""")

allfreq = []
t5overfreq = []
t5underfreq = []
for row in cursor:
    allfreq.append( row[2] / float(row[1]) * 100.0)
    t5overfreq.append( row[3] / float(row[4]) * 100.0)
    t5underfreq.append( row[5] / float(row[6]) * 100.0)

allfreq= np.array(allfreq)
t5overfreq= np.array(t5overfreq)
t5underfreq= np.array(t5underfreq)

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

ax.plot(np.arange(1,365), smooth(allfreq[:-2],14), c='g', label='All Cases')
ax.plot(np.arange(1,365), smooth(t5overfreq[:-2],14), c='r', label='+5 $^\circ$F')
ax.plot(np.arange(1,365), smooth(t5underfreq[:-2],14), c='b', label='-5 $^\circ$F')
ax.grid(True)
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_title("1933-2012 Des Moines 3 PM Temps and Winds\nAir Temperature +/- 5$^\circ$F over average and 10+ mph winds")
ax.set_ylabel("Frequency [%]")
ax.set_xlabel("Day of Year, 14 day centered smoothing applied")
ax.set_xlim(1,366)
ax.legend(loc=4)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')