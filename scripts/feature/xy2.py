import numpy
from scipy import stats

import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
POSTGIS = iemdb.connect('postgis', bypass=True)
pcursor = POSTGIS.cursor()


ccursor.execute("""
 select year, sum(precip) from alldata_ia where station = 'IA0000'
 and month in (4,5) and sday < '0509'
 and day >= '1986-01-01' GROUP by year ORDER by year ASC 
""")
x = []
for row in ccursor:
    x.append( float(row[1]) )

pcursor.execute("""
 SELECT yr, count(*) from
 (SELECT distinct wfo, eventid, phenomena, extract(year from issue) as yr
 FROM warnings where gtype = 'C' and substr(ugc,1,3) = 'IAC' and 
 significance = 'W' and phenomena in ('SV') and 
(extract(month from issue) = 4 or (extract(month from issue) = 5 and 
 extract(day from issue) < 9))) as foo
 GROUP by yr ORDER by yr ASC
""")
y = []
for row in pcursor:
    y.append( float(row[1]) )

print x, len(x)
print y, len(y)


from matplotlib import pyplot as plt

#h_slope, intercept, h_r_value, p_value, std_err = stats.linregress(snowd, diff)
#print h_slope, intercept, h_r_value, p_value, std_err

fig = plt.figure()
ax = fig.add_subplot(111)

def g(y):
  if y == 2002:
    return 'right'
  return 'center'

ax.scatter(x, y)
for xi, yi, ti in zip(x, y, range(1986,2014)):
  if yi < 25 or yi > 100 or ti == 2013:
    ax.text(xi, yi + 2, "%s" % (ti,), ha=g(ti), va='bottom')
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
ax.set_title("1986-2013 1 April - 7 May :: Precipitation + Severe Weather")
ax.set_xlabel("Iowa Statewide Precipitation [inch]")
ax.set_ylabel("Severe Thunderstorm Warnings")
ax.set_ylim(bottom=0)
#ax.set_xlim(60,90)
#ax.set_ylim(10,35)
#ax.set_yticks( range(0,30,6))
#ax.set_xticks( range(0,60,6))
#ax.legend(loc='best')
ax.grid(True)
import iemplot
fig.savefig('test.svg')
iemplot.makefeature('test')
