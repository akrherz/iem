import numpy
from scipy import stats

import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()


ccursor.execute("""
 select year, sum(case when station = 'IA2203' then sum else 0 end), 
 avg(case when station != 'IA2203' then sum else null end) as a 
 from (select station, year, sum(precip) from alldata_ia 
 where month = 6 and 
 station in ('IA2203', 'IA1319', 'IA2724', 'IA2364', 'IA1063') and year > 1950
 GROUP by station, year) as foo GROUP by year ORDER by year ASC
""")
x = []
y = []
for row in ccursor:
    x.append( float(row[1]) )
    y.append( float(row[2]) )

x[-1] = 3.61

from matplotlib import pyplot as plt

#h_slope, intercept, h_r_value, p_value, std_err = stats.linregress(snowd, diff)
#print h_slope, intercept, h_r_value, p_value, std_err

fig = plt.figure()
ax = fig.add_subplot(111)

def g(y):
    if y in [1993,]:
        return 'left'
    return 'center'

ax.scatter(x, y)
ax.plot([0,14], [0,14])
for xi, yi, ti in zip(x, y, range(1951,2015)):
  if yi > 9 or xi > 9 or ti == 2014:
    ax.text(xi, yi + 0.1, "%s" % (ti,), ha=g(ti), va='bottom')
#ax.scatter(x[-1],y[-1], facecolor='r', label='2012')
#ax.plot([x[-1],x[-1]], [10,35], color='r')
#ax.text( x[-1], 13, '2012', color='r')
#for i in range(len(years)):
#    if y[i] > x[i]:
#        ax.text(x[i]-0.4, y[i], "%.0f" % (years[i],), ha='right')
#ax.scatter(18, -4.5, color='g', marker='+', s=100)
#ax.plot( [60,90], [60,90], color='k')

#ax.text(26, 56, "Average", ha='center', va='center', color='g')
#ax.plot( [20,80], [58,58], color='g')
#ax.plot( [0,31], [intercept, intercept + 31 * h_slope], color='r',
#         label=r"Fit = $\frac{%.2f ^{\circ}\mathrm{F}}{day}, R^2 = %.2f$" % (
#                                h_slope, h_r_value ** 2))
ax.set_title("1951-2014 June Precipitation\nBurlington, Cedar Rapids, Dubuque, Estherville Avg vs Des Moines ")
ax.set_xlabel("Des Moines Precipitation [inch], *2014 thru 24 June")
ax.set_ylabel("Four City (non-DSM) Precip Average [inch]")
ax.set_ylim(0,14)
ax.set_xlim(0,14)
#ax.set_xlim(60,90)
#ax.set_ylim(10,35)
#ax.set_yticks( range(0,30,6))
#ax.set_xticks( range(0,60,6))
#ax.legend(loc='best')
ax.grid(True)
import iemplot
fig.savefig('test.ps')
iemplot.makefeature('test')
