import iemdb 
import numpy as np
import datetime
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

def smooth(x,window_len=14,window='hanning'):

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
        w=ones(window_len,'d')
    else:
        w=eval('np.'+window+'(window_len)')

    y=np.convolve(w/w.sum(),s,mode='same')
    return y[window_len-1:-window_len+1]


ccursor.execute("""
 select extract(doy from day) as doy, 
  sum(case when high - low > 29 then 1 else 0 end), 
  sum(case when high - low > 34 then 1 else 0 end), 
  sum(case when high - low > 19 then 1 else 0 end), 
  count(*) from alldata_ia where station = 'IA0200' GROUP by doy
""")

cnts = np.zeros( (366,) , 'f')
cnts35 = np.zeros( (366,) , 'f')
cnts20 = np.zeros( (366,) , 'f')
for row in ccursor:
  cnts[ int(row[0]) - 1 ] = row[1] / float(row[4]) * 100.0
  cnts35[ int(row[0]) - 1 ] = row[2] / float(row[4]) * 100.0
  cnts20[ int(row[0]) - 1 ] = row[3] / float(row[4]) * 100.0


import matplotlib.pyplot as plt
import mx.DateTime
fig = plt.figure()
ax = fig.add_subplot(111)

ax.bar(np.arange(0,366) - 0.5, cnts20, ec='tan', fc='tan', label="20+ $^{\circ}\mathrm{F}$")
ax.bar(np.arange(0,366) - 0.5, cnts, ec='b', fc='b', label="30+ $^{\circ}\mathrm{F}$")
ax.bar(np.arange(0,366) - 0.5, cnts35, ec='r', fc='r', label='35+ $^{\circ}\mathrm{F}$')

ax.grid(True)
ax.set_ylabel("Observed Frequency [%]")
ax.set_title("Ames Daily Frequency of Difference\nbetween High + Low Temp [1893-2011]")
ax.set_xlim(-0.4,366)
ax.set_ylim(0,100)
xticks = []
xticklabels = []
for i in range(0,366):
  ts = mx.DateTime.DateTime(2000,1,1) + mx.DateTime.RelativeDateTime(days=i)
  if ts.day == 1:
    xticks.append(i)
    xticklabels.append( ts.strftime("%b") )
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)
#ax.annotate("Chances are\nnot good", xy=(306, pltdata[306]),  xycoords='data',
#                xytext=(10, 30), textcoords='offset points',
#                bbox=dict(boxstyle="round", fc="0.8"),
#                arrowprops=dict(arrowstyle="->",
#               connectionstyle="angle3,angleA=0,angleB=-90"))
ax.legend(ncol=1,loc=2)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
