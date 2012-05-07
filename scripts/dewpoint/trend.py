import matplotlib.pyplot as plt
import numpy
import mesonet
import math
from scipy import stats
import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=12)
import iemdb
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

SYEAR = 1970

def get_data(station):
    data = []
    for yr in range(SYEAR,2012):
        acursor.execute("""
        SELECT valid + '10 minutes'::interval, tmpf, dwpf from t%s WHERE station = '%s'
        and extract(year from valid + '0 month'::interval) = %s 
        and extract(month from valid) in (6,7,8) and dwpf > -30 and tmpf > -30
        """ % (yr, station, yr))
        tot = 0
        for row in acursor:
            dwpc = mesonet.f2c( row[2] )
            e  = 6.112 * math.exp( (17.67 * dwpc) / (dwpc + 243.5))
            mixr =  0.62197 * e / (1000.0 - e)
            if mixr > 0:
                tot += mixr
        data.append( tot / float(acursor.rowcount) * 1000.0)
    return numpy.array( data )



years = numpy.arange(SYEAR,2012)

fig = plt.figure(figsize=(8,6))
ax = fig.add_subplot(111)

ax2 = ax.twinx()
def h2opsat(t):
    pwat=6.107799961 + t*(4.436518521e-1 + t*(1.428945805e-2 + t*(2.650648471e-4 + t*(3.031240396e-6 + t*(2.034080948e-8 + t*6.136820929e-11)))))
    pice=6.109177956 + t*(5.034698970e-1 + t*(1.886013408e-2 + t*(4.176223716e-4 + t*(5.824720280e-6 + t*(4.838803174e-8 + t*1.838826904e-10)))))
    return min(pwat,pice)

def dewpoint(t,ph2o):
    
    while (h2opsat(t)>=ph2o):
        t -= 0.1
    return t
def conv(mixr):
    spc = mixr / (1 + mixr / 1000.0 )
    vmr = 28.9644 / (28.9644 - 18.01534 * ( 1.0 - 1000.0 / spc))
    ph2o = vmr * 1012.5
    dwpc = dewpoint(35,ph2o)
    return mesonet.c2f( dwpc )
def update_ax2(ax1):
   y1, y2 = ax1.get_ylim()
   ax2.set_ylim(conv(y1), conv(y2))
   ax2.figure.canvas.draw()
ax.callbacks.connect("ylim_changed", update_ax2)

ax.set_xlim(SYEAR - 0.5,2011.5)
stations = {'DSM': {'name':'Des Moines', 'color': 'r', 'marker': '^'}, 
            #'STL': {'name': 'Saint Louis', 'color': 'b', 'marker': 'x'}, 
            #'MCI': {'name': 'Kansas City', 'color': 'g', 'marker': 'o'}
            }
for station in stations.keys():
    data = get_data(station)

    h_slope, intercept, h_r_value, p_value, std_err = stats.linregress(years, data)
    trend = numpy.array( data )
    for yr in range(SYEAR,2012):
        trend[yr-SYEAR] = intercept + (yr) * h_slope
    ax.scatter(years, data, facecolor='%s'% (stations[station]['color'],),
               marker='%s'% (stations[station]['marker'],), s=60,
               label="%s %.2f$^{\circ}\mathrm{F}$/decade\n$R^2$: %.2f" % (stations[station]['name'],
                                               (trend[9] - trend[0]), h_r_value**2 ))
    ax.plot( years, trend, color='%s'% (stations[station]['color'],))

ax.set_title("%s-2011 June July August Dew Point Trends" % (SYEAR,))
ax.set_ylabel("Mean Mixing Ratio [g/kg]")
ax2.set_ylabel("Dew Point $^{\circ}\mathrm{F}$")
ax.set_ylim(10,17)
ax.legend(prop=prop, ncol=2)
ax.grid()
#ax.set_ylim(10,17)
"""
ax2 = fig.add_subplot(312)

bars = ax2.bar(years-0.4, vals - numpy.average(vals), edgecolor='b', facecolor='b')
for bar in bars:
    if bar.get_y() < 0:
        bar.set_edgecolor('r')
        bar.set_facecolor('r')
ax2.set_title("Mid-West July Departure from Average")
ax2.set_ylabel("Mixing Ration [g/kg]")
#ax2.set_ylim(8,14)
ax2.grid(True)
ax2.set_xlim(1950.5,2011.5)

ax3 = fig.add_subplot(212)

bars = ax3.bar(years-0.4, vals - trend, edgecolor='b', facecolor='b')
for bar in bars:
    if bar.get_y() < 0:
        bar.set_edgecolor('r')
        bar.set_facecolor('r')
        
ax3.set_title("Departure from Trend")
ax3.set_ylabel("Mixing Ratio [g/kg]")
ax3.grid(True)
ax3.set_xlim(1950.5,2011.5)
"""
#ax3.set_xlabel("*2011 total thru 26 July")
fig.savefig('test.png')
#import iemplot
#iemplot.makefeature('test')


