import psycopg2
import numpy as np
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()

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

cursor.execute("""

 SELECT sday, sum(case when (narr_srad < (0.75 * thres) and
  narr_srad < (0.75 * thres) and narr_srad < (0.75 * thres)) then 1 else 0 end),
  max(thres), max(case when year = 2013 then coalesce(narr_srad, merra_srad, hrrr_srad *1.1) else 0 end) from
 (SELECT sday, year, merra_srad, hrrr_srad,  narr_srad, max(narr_srad) OVER (partition by sday) as thres,
 lag(narr_srad) OVER (ORDER by day ASC),  
 lead(narr_srad) OVER (ORDER by day ASC)
 from alldata_ia where 
 station = 'IA0200'  and year > 1978) as foo
 GROUP by sday ORDER by sday ASC
 """)

y = []
y2 = []
for row in cursor:
    y.append( row[2] )
    y2.append( row[3] )
    print row[0], row[3]
y = np.array(y)
y2 = np.array(y2)
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

smoothed = smooth(y,5)
ax.fill_between(range(1,367), 0, smoothed, color='tan', label="Max")
bars = ax.bar(range(366), np.where(y2 > smoothed, smoothed, y2), fc='g', ec='g', label="2013")
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlim(0,366)
ax.set_xlabel("thru 16 Oct 2013")
ax.set_title("Ames Daily Solar Radiation\n1979-2012 NARR Climatology w/ 2013 NARR + HRRR Estimates")
ax.legend()
ax.grid(True)
ax.set_ylabel("Shortwave Solar Radiation $MJ$ $d^{-1}$")
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')