import iemdb
import numpy as np
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
import mx.DateTime
import scipy.stats

corr = []
slope = []
sts = mx.DateTime.DateTime(2001,1,1)
ets = mx.DateTime.DateTime(2002,1,1)
now = sts
while now < ets:
    ccursor.execute("""
    SELECT high, low from alldata where stationid = 'ia0200' and sday = %s
    """, (now.strftime("%m%d"),))
    highs = []
    lows = []
    for row in ccursor:
        highs.append( row[0] )
        lows.append( row[1] )
    corr.append( scipy.stats.corrcoef(highs, lows)[0,1] )
    h_slope, intercept, h_r_value, p_value, std_err = scipy.stats.linregress(lows, highs)
    slope.append( h_slope )
    now += mx.DateTime.RelativeDateTime(days=1)
    
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(211)
ax.set_title("Ames Daily High & Low Temperature\n(1893-2010)")
ax.set_ylim(0.4,0.9)
ax.set_ylabel("Correlation Coefficient")
ax.plot( np.arange(1,366), corr, drawstyle='step')

ax.set_xlim(0,366)
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.grid()

ax = fig.add_subplot(212)
ax.plot( np.arange(1,366), slope, drawstyle='step')

ax.set_xlim(0,366)
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_ylabel("Linear Regress Slope High/Low")
ax.grid()


fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')