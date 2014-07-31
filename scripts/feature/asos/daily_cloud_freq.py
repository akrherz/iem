import iemdb
import numpy

def smooth(x,window_len=11,window='hanning'):
    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"


    s=numpy.r_[2*x[0]-x[window_len:1:-1],x,2*x[-1]-x[-1:-window_len:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=ones(window_len,'d')
    else:
        w=eval('numpy.'+window+'(window_len)')

    y=numpy.convolve(w/w.sum(),s,mode='same')
    return y[window_len-1:-window_len+1]


def doit(hr):
    ASOS = iemdb.connect('asos', bypass=True)
    acursor = ASOS.cursor()

    acursor.execute("""
SELECT extract(doy from d) as doy, count(*) from
 (SELECT date(valid) as d, 
  sum( case when skyc1 in ('BKN','OVC') or skyc2 in ('BKN','OVC') or 
        skyc3 in ('BKN','OVC') then 1 else 0 end ) as clouds, 
  max(tmpf) as high, max(dwpf) as maxd,
  max(sknt) as wind from alldata where 
  station = 'DSM' and tmpf > -50 and sknt >= 0 and 
  valid > '1973-01-01' and valid < '2010-01-01' 
  and extract(hour from valid) = %s GROUP by d
  ) as foo
WHERE clouds > 0 GROUP by doy ORDER by doy ASC
  """, (hr,))
    doy = []
    for row in acursor:
        doy.append( row[1] )
    return numpy.array( doy )

data  = numpy.zeros( (24,365), 'f')
for i in range(24):
    data[i,:] = doit(i)[:365] / 37.0 * 100.0
#doy = [6L, 9L, 7L, 5L, 8L, 7L, 10L, 4L, 3L, 3L, 4L, 4L, 6L, 4L, 3L, 5L, 4L, 2L, 6L, 4L, 10L, 4L, 5L, 8L, 5L, 4L, 5L, 5L, 5L, 6L, 18L, 13L, 8L, 16L, 15L, 13L, 11L, 12L, 8L, 9L, 9L, 11L, 10L, 12L, 8L, 11L, 13L, 12L, 9L, 14L, 14L, 10L, 14L, 12L, 8L, 16L, 7L, 5L, 9L, 9L, 8L, 11L, 9L, 8L, 10L, 13L, 11L, 11L, 5L, 7L, 8L, 7L, 13L, 11L, 12L, 8L, 11L, 7L, 7L, 10L, 10L, 5L, 9L, 5L, 9L, 7L, 7L, 5L, 9L, 6L, 7L, 9L, 11L, 11L, 12L, 11L, 11L, 10L, 13L, 11L, 6L, 7L, 10L, 11L, 13L, 12L, 12L, 11L, 9L, 5L, 12L, 16L, 11L, 13L, 14L, 9L, 8L, 10L, 13L, 7L, 6L, 12L, 10L, 12L, 12L, 14L, 5L, 9L, 9L, 6L, 9L, 10L, 9L, 7L, 13L, 12L, 13L, 18L, 16L, 16L, 11L, 11L, 8L, 7L, 8L, 12L, 8L, 10L, 9L, 9L, 13L, 10L, 11L, 8L, 9L, 13L, 10L, 13L, 10L, 12L, 13L, 10L, 6L, 15L, 12L, 11L, 10L, 8L, 9L, 12L, 7L, 11L, 18L, 19L, 9L, 17L, 17L, 15L, 19L, 24L, 15L, 15L, 14L, 10L, 9L, 18L, 17L, 14L, 12L, 18L, 14L, 18L, 14L, 15L, 18L, 20L, 19L, 13L, 8L, 12L, 13L, 14L, 20L, 19L, 15L, 13L, 17L, 10L, 15L, 16L, 16L, 16L, 15L, 17L, 15L, 15L, 7L, 16L, 14L, 19L, 13L, 12L, 18L, 16L, 17L, 17L, 12L, 16L, 16L, 12L, 13L, 13L, 17L, 18L, 18L, 14L, 21L, 16L, 16L, 18L, 17L, 18L, 20L, 14L, 17L, 25L, 29L, 15L, 26L, 21L, 24L, 16L, 20L, 21L, 15L, 13L, 15L, 16L, 20L, 18L, 17L, 15L, 10L, 9L, 12L, 13L, 13L, 25L, 19L, 21L, 22L, 23L, 14L, 19L, 18L, 19L, 21L, 19L, 19L, 16L, 11L, 15L, 20L, 18L, 21L, 11L, 15L, 18L, 14L, 18L, 15L, 15L, 14L, 15L, 17L, 14L, 17L, 17L, 13L, 16L, 15L, 10L, 8L, 9L, 9L, 13L, 7L, 10L, 9L, 19L, 14L, 6L, 10L, 12L, 5L, 8L, 10L, 11L, 6L, 8L, 12L, 6L, 9L, 8L, 6L, 12L, 8L, 10L, 8L, 6L, 7L, 10L, 9L, 3L, 9L, 8L, 7L, 5L, 3L, 9L, 10L, 10L, 14L, 11L, 11L, 4L, 10L, 9L, 11L, 9L, 11L, 8L, 10L, 5L, 10L, 8L, 9L, 7L, 10L, 7L, 6L, 6L, 8L, 8L, 7L, 3L]

import matplotlib.pyplot as plt


fig = plt.figure()
ax = fig.add_subplot(111)

res = ax.imshow( data, aspect='auto', rasterized=True)
fig.colorbar(res)

"""
ax.plot( numpy.arange(0,366), smooth(doy8,3, 'hamming') / 61.0, c='b', label='8 AM')
ax.plot( numpy.arange(0,366), smooth(doy12,3,'hamming') / 61.0, c='green', label='Noon')
ax.plot( numpy.arange(0,366), smooth(doy16,3,'hamming')  / 61.0, c='r', label='4 PM')
#ax.plot( numpy.arange(0,366), smooth(doy0,3,'hamming') / 61.0, c='green', label='Mid')
#ax.plot( numpy.arange(0,366), smooth(doy4,3,'hamming') / 61.0, c='purple', label='4 AM')
"""
ax.set_xticks( (1,31,59,90,120,151,181,212,243,274,303,334) )
ax.set_xticklabels( ("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec") )
ax.set_xlim(0,356)

ax.set_ylim(-0.5,23.5)
ax.set_yticks((0,4,8,12,16,20))
ax.set_yticklabels( ('Mid', '4 AM', '8 AM', 'Noon', '4 PM', '8 PM'))
#ax.legend()

ax.set_title("Des Moines [1973-2009] Frequency of Cloudiness [%]\n(broken or overcast reported)")

import iemplot
fig.savefig('test.ps')
iemplot.makefeature('test')