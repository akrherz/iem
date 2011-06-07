
from matplotlib import pyplot as plt
import numpy
import iemplot
import iemdb
POSTGIS = iemdb.connect('postgis', bypass=True)
acursor = POSTGIS.cursor()

acursor.execute("""
select extract(year from issued) as yr, count(*) from watches where 
extract(month from issued) in (1,2,3) GROUP by yr ORDER by yr ASC
""")
apr1 = []
years = []
#totals = []
for row in acursor:
  years.append( row[0] )
  apr1.append( row[1] )

acursor.execute("""
select extract(year from issued) as yr, count(*) from watches GROUP by yr ORDER by yr ASC
""")
full = []
#totals = []
for row in acursor:
  full.append( row[1] )

full = numpy.array(full)
apr1= numpy.array(apr1)
years = numpy.array(years)

fig = plt.figure()
ax = fig.add_subplot(111)

ax.bar(years -0.4, apr1, color='r', label="Prior 1 Apr")
ax.bar(years -0.4, full-apr1, bottom=apr1, color='b', label="After 1 Apr")
#ax.plot( [1989,2011], [1.49, 1.49], color='r', label='Average 1.49')
#rects2 = ax.bar(numpy.arange(2005,2011), onetwenty, 0.33, color='r', label=('2 hour'))
#ax.set_xticklabels( numpy.arange(1990,2011) )
ax.set_xlim(1996.5, 2011.5)
ax.set_ylim(0,1100)
#rects1[-1].set_facecolor('r')
ax.legend(loc=2)
#ax.set_xticks( (0,6,12,18,24,30) )
#ax.set_xticklabels( ('Mid\n29 Dec', '6 AM', 'Noon', '6 PM', 'Mid\n30 Dec', '6 AM'))

#for i in range(6):
#  label = "%s, %.2f" % (sixtyl[i], sixty[i])
#  ax.text( 2005 + i - 0.15, 0.05, label, color='white',
#                ha='center', va='bottom', rotation=90, fontsize=16)
#  label = "%s, %.2f" % (onetwentyl[i], onetwenty[i])
#  ax.text( 2005 + i + 0.17, 0.05, label, color='white',
#                ha='center', va='bottom', rotation=90, fontsize=16)
#

ax.set_ylabel("Number of Watches")
ax.set_xlabel("Year, 2011 data to 1 Apr")
ax.set_title("Storm Prediction Center Severe T'storm/Tornado Watches")
ax.grid(True)
plt.savefig('test.ps')
iemplot.makefeature("test")
