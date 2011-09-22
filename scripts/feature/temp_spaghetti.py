import matplotlib.pyplot as plt
import matplotlib.font_manager 
import numpy
prop = matplotlib.font_manager.FontProperties(size=10) 
from pyIEM import mesonet
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_xlim(0,1443)
xticks = []
xticklabels = []
for x in range(0,25,2):
    xticks.append( x * 60 )
    if x == 0 or x == 24:
        lbl = 'Mid'
    elif x == 12:
        lbl = 'Noon'
    else:
        lbl = x % 12
    xticklabels.append(lbl)
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)
#ax.set_xlabel("Local Hour of Day [CDT]")
#ax.set_ylabel("Air & Dew Point (dash) Temp [F]", fontsize=9)
ax.set_title("2011 Des Moines (KDSM) Failures to reach 100$^{\circ}\mathrm{F}$")
ax.set_ylabel("Air Temperature $^{\circ}\mathrm{F}$")
ax.set_xlabel("* 15 minute flat smoothing applied")

def smooth(x,window_len=11,window='hanning'):
    """smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
        
    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)
    
    see also: 
    
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an array instead of a string   
    """

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

import iemdb
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

# Extract 100 degree obs
icursor.execute("""
 SELECT day from summary_2011 where station = 'DSM' and max_tmpf = 99
 ORDER by day ASC
""")
maxD = 0
colors = ['r','b','green']
diff = 0.0
w = numpy.bartlett(15)
for row in icursor:
    d = row[0]
    print d
    acursor.execute("""
        SELECT valid, tmpf  from t%s_1minute WHERE station = 'DSM' and valid BETWEEN
        '%s 00:00' and '%s 23:59'::timestamp
        and tmpf > -50 ORDER by valid ASC
        """ % (d.year, d, d))
    times = []
    tmpf = []
    dwpf = []
    raining = False
    for row2 in acursor:
        
        times.append( row2[0].hour * 60 + row2[0].minute )
        tmpf.append( row2[1] )
    tmpf = numpy.array( tmpf )
        #dwpf.append( row2[3] )
    #diff += tot2 - tot
    #c = '#E8AFAF'
    #if raining:
    #    c = 'b'
    #c = colors.pop()
    ax.plot(smooth(tmpf, window_len=15, window='flat'),  label= d.strftime("%d %B") )
    #ax.plot(times, dwpf, linestyle='--', c=c)
#ax.text(6*60, 67, "6-10 AM Diff: %.1f$^{\circ}\mathrm{F}$" % ((diff/3.,) ))
#ax.text(14*60, 67, "Marshalltown, IA (KMIW ASOS)")
ax.set_ylim(74,100)
ax.grid(True)
ax.legend(loc=2, prop=prop)

import iemplot
fig.savefig('test.ps')

iemplot.makefeature('test')
