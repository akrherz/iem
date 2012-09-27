import numpy
from scipy import stats

import iemdb
COOP = iemdb.connect('asos', bypass=True)
ccursor = COOP.cursor()


#select foo.year, foo.april, foo2.march from (select year, avg(high) as april from alldata where stationid = 'ia2203' and month = 4 and sday < '0408' GROUP by year) as foo, (select year, avg(high) as march from alldata where stationid = 'ia2203' and sday > '0323' and sday < '0401' GROUP by year) as foo2 where foo.year = foo2.year
ccursor.execute("""
 select extract(year from valid) as yr, 
 max(case when extract(month from valid) = 8 then dwpf else 0 end) - 
 max(case when extract(month from valid) = 9 then dwpf else 0 end) as d, 
 max(case when extract(month from valid) = 8 then dwpf else 0 end) as a,
 max(case when extract(month from valid) = 9 then dwpf else 0 end) from alldata 
 where station = 'DSM' GROUP by yr ORDER by yr ASC
""")
x = []
y = []
years = []
for row in ccursor:
    if row[2] > 10:
        x.append( float(row[2]) )
        y.append( float(row[3]) )
        years.append( row[0] )
    
from matplotlib import pyplot as plt

#h_slope, intercept, h_r_value, p_value, std_err = stats.linregress(snowd, diff)
#print h_slope, intercept, h_r_value, p_value, std_err

fig = plt.figure()
ax = fig.add_subplot(111)

ax.scatter(x, y)
ax.scatter(x[-1],y[-1], facecolor='r', label='2012')
for i in range(len(years)):
    if y[i] > x[i]:
        ax.text(x[i]-0.4, y[i], "%.0f" % (years[i],), ha='right')
#ax.scatter(18, -4.5, color='g', marker='+', s=100)
ax.plot( [60,90], [60,90], color='k')

#ax.text(26, 56, "Average", ha='center', va='center', color='g')
#ax.plot( [20,80], [58,58], color='g')
#ax.plot( [0,31], [intercept, intercept + 31 * h_slope], color='r',
#         label=r"Fit = $\frac{%.2f ^{\circ}\mathrm{F}}{day}, R^2 = %.2f$" % (
#                                h_slope, h_r_value ** 2))
ax.set_title("Des Moines Monthly Maximum Dew Point [1933-3 Sep 2012]")
ax.set_xlabel("Maximum August Dew Point $^{\circ}\mathrm{F}$")
ax.set_ylabel("Maximum September Dew Point $^{\circ}\mathrm{F}$")
ax.set_xlim(60,90)
ax.set_ylim(60,90)
#ax.set_yticks( range(0,30,6))
#ax.set_xticks( range(0,60,6))
#ax.legend(loc='best')
ax.grid(True)
import iemplot
fig.savefig('test.ps')
iemplot.makefeature('test')
