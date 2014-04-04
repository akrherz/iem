import iemdb
import numpy as np
from scipy import stats
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

doy = []
years = []
maxes = np.zeros( (2015-1893), 'f')
ccursor.execute("""
 select year, extract(doy from day), 
 max(extract(doy from day)) OVER (PARTITION by year) from alldata_ia 
 where station = 'IA0200' and month < 7 and high < 32
""")
for row in ccursor:
    doy.append( row[1] )
    years.append( row[0] )
    maxes[ row[0] - 1893 ] = row[2]
years.append(2014)
doy.append(84)
years= np.array( years )
doy = np.array( doy )
maxes = np.array( maxes )
    
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1, 1)

ax.scatter(doy, years, marker='s', facecolor='b', edgecolor='b')
ax.scatter(doy[-1], years[-1], marker='o', facecolor='r', edgecolor='r')
ax.set_title("1893-2014 Ames Days with High Temp Below Freezing")
ax.grid(True)

h_slope, intercept, r_value, p_value, std_err = stats.linregress(np.arange(1893,2015),
                                                                 maxes)
y1 = 1893 * h_slope + intercept
y2 = 2014 * h_slope + intercept
print intercept, h_slope, maxes
ax.plot([y1,y2], [1893,2014], lw=3, color='k', zorder=2)
ax.plot([y1,y2], [1893,2014], lw=1, color='yellow', zorder=3)
ax.text(100,1900, r"Slope=-4.6 $\frac{days}{100yrs}$")
ax.text(100,1910, r"R$^2$=%.2f" % (r_value ** 2,) )
ax.set_ylim(1892.5, 2015.5)
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlim(0,140)
ax.set_xlabel("* 2014 thru 25 March")
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')