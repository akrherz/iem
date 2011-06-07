import numpy
from scipy import stats

import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()


#select foo.year, foo.april, foo2.march from (select year, avg(high) as april from alldata where stationid = 'ia2203' and month = 4 and sday < '0408' GROUP by year) as foo, (select year, avg(high) as march from alldata where stationid = 'ia2203' and sday > '0323' and sday < '0401' GROUP by year) as foo2 where foo.year = foo2.year
ccursor.execute("""
select year, sum( case when sday < '0523' and high > 69 then 1 else 0 end), sum(case when sday > '0523' and high > 89 then 1 else 0 end ) from alldata where stationid = 'ia0200' and year < 2011 GROUP by year ORDER by year DESC
""")
x = []
y = []
y2 = []
x2 = []
for row in ccursor:
    if row[0] < 1990:
        x2.append( float(row[1]) )
        y2.append( float(row[2]) )
    else:
        x.append( float(row[1]) )
        y.append( float(row[2]) )
    
from matplotlib import pyplot as plt

#h_slope, intercept, h_r_value, p_value, std_err = stats.linregress(snowd, diff)
#print h_slope, intercept, h_r_value, p_value, std_err

fig = plt.figure()
ax = fig.add_subplot(111)

ax.scatter(x, y, label="After 1990")
ax.scatter(x2, y2, color='r', label="Prior 1990")
#ax.scatter(18, -4.5, color='g', marker='+', s=100)
ax.text(15, 55, "2011", ha='center', va='center', color='b')
ax.plot( [15,15], [0,70], color='b')

#ax.text(26, 56, "Average", ha='center', va='center', color='g')
#ax.plot( [20,80], [58,58], color='g')
#ax.plot( [0,31], [intercept, intercept + 31 * h_slope], color='r',
#         label=r"Fit = $\frac{%.2f ^{\circ}\mathrm{F}}{day}, R^2 = %.2f$" % (
#                                h_slope, h_r_value ** 2))
ax.set_title("Ames Daily High Temperatures [1893-2010]")
ax.set_xlabel("Days prior to 23 May above 70 F")
ax.set_ylabel("Days after 23 May above 90 F")
ax.set_xlim(-0.5,50)
ax.set_ylim(-0.5,70)
#ax.set_yticks( range(0,30,6))
#ax.set_xticks( range(0,60,6))
ax.legend()
ax.grid(True)
import iemplot
fig.savefig('test.ps')
iemplot.makefeature('test')
