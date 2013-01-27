import numpy
from scipy import stats

import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()


#select foo.year, foo.april, foo2.march from (select year, avg(high) as april from alldata where stationid = 'ia2203' and month = 4 and sday < '0408' GROUP by year) as foo, (select year, avg(high) as march from alldata where stationid = 'ia2203' and sday > '0323' and sday < '0401' GROUP by year) as foo2 where foo.year = foo2.year
ccursor.execute("""
 select year, sum(precip) from alldata_ia where station = 'IA0000'
 and month > 2 and month < 12 
 and day >= '1893-01-01' GROUP by year ORDER by year ASC 
""")
x = []
for row in ccursor:
    x.append( float(row[1]) )

ccursor.execute("""
 select extract(year from day + '1 month'::interval) as yr, 
 avg((high+low)/2.) from alldata_ia where station = 'IA0000'
 and month in (12,1,2) and day >= '1893-12-01' 
 and day < '2012-12-01' GROUP by yr ORDER by yr ASC 
""")
y = []
for row in ccursor:
    y.append( float(row[1]) )



from matplotlib import pyplot as plt

#h_slope, intercept, h_r_value, p_value, std_err = stats.linregress(snowd, diff)
#print h_slope, intercept, h_r_value, p_value, std_err

fig = plt.figure()
ax = fig.add_subplot(111)

ax.scatter(x[:-1], y)
#ax.scatter(x[-1],y[-1], facecolor='r', label='2012')
ax.plot([x[-1],x[-1]], [10,35], color='r')
ax.text( x[-1], 13, '2012', color='r')
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
ax.set_title("Mar-Nov Iowa Precip and following Dec-Feb Avg Temp 1893-2011")
ax.set_xlabel("March-November Precipitation [inch]")
ax.set_ylabel("December-February Average Temp $^{\circ}\mathrm{F}$")
#ax.set_xlim(60,90)
ax.set_ylim(10,35)
#ax.set_yticks( range(0,30,6))
#ax.set_xticks( range(0,60,6))
#ax.legend(loc='best')
ax.grid(True)
import iemplot
fig.savefig('test.ps')
iemplot.makefeature('test')
