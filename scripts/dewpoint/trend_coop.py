import matplotlib.pyplot as plt
import numpy
import mesonet
import math
from scipy import stats
import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=12)
import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

SYEAR = 1970

def get_data(station):
    data = []
    ccursor.execute("""
    SELECT year, avg(low) from alldata_ia where station = '%s' and 
    month in (7,8) and year >= %s and year < 2012 
    GROUP by year ORDER by year ASC
    """ % (station, SYEAR))
    for row in ccursor:
        data.append( float(row[1]) )
    return numpy.array( data )



years = numpy.arange(SYEAR,2012)

fig = plt.figure(figsize=(8,6))
ax = fig.add_subplot(111)

ax.set_xlim(SYEAR - 0.5,2011.5)
stations = {'IA2203': {'name':'Des Moines', 'color': 'r', 'marker': '^'}, 
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

ax.set_title("%s-2011 July August Daily Minimum Temperature Trends" % (SYEAR,))
ax.set_ylabel("Min Temperature $^{\circ}\mathrm{F}$")
#ax.set_ylim(10,17)
ax.legend(prop=prop, ncol=2, loc=2)
ax.grid()
#ax.set_ylim(52,64)
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


