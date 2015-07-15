import iemdb
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()
import mx.DateTime

years = []
wind = []
highs = []
for yr in range(1971,2011):
    sep1 = mx.DateTime.DateTime(yr,9,1)
    labor = sep1 + mx.DateTime.RelativeDateTime(weekday=(mx.DateTime.Monday,1))
    print labor
    acursor.execute("""
    SELECT avg(sknt), max(tmpf) from t%s WHERE station = 'DSM' and valid BETWEEN '%s 00:00' and '%s 00:00'
    and sknt >= 0
    """ % (yr, labor.strftime("%Y-%m-%d"), (labor + mx.DateTime.RelativeDateTime(days=1)).strftime("%Y-%m-%d")))
    row = acursor.fetchone()
    years.append(yr)
    wind.append( row[0] )
    highs.append( row[1] )
    print yr, row
highs.append(73)
wind.append( 8 )
years.append(2011)

import numpy
import matplotlib.pyplot as plt

years = numpy.array( years )
highs = numpy.array( highs )

fig = plt.figure()
ax = fig.add_subplot(211)
rects = ax.bar( years - 0.4, highs )
rects[-1].set_facecolor('red')
ax.plot([years[0],years[-1]], [numpy.average(highs), numpy.average(highs)], color='r')
#for rect, label in zip(rects, labels):
#  y = rect.get_height()
#  x = rect.get_x()
#  ax.text(x+0.3,y-5,label.strftime("%b %-d"), weight='bold', rotation=90, color='white')
ax.set_xlim(1970.5, 2011.5)
ax.set_ylim(50,100)
#ax.set_yticks((91,121,152))
#ax.set_yticklabels(('Apr 1', 'May 1', 'Jun 1'))

ax.set_ylabel("High Temperature [F]")
#ax.set_xlabel("*2011 Total of 106 hours is the least")
ax.grid(True)
#ax.set_ylim(35,75)
ax.set_title("Des Moines: 1971-2010 Labor Days")

ax2 = fig.add_subplot(212)
rects = ax2.bar( years - 0.4, wind )
rects[-1].set_facecolor('red')
ax2.set_xlim(1970.5, 2011.5)
ax2.set_ylabel("Average Wind Speed [kts]")
ax2.grid(True)
ax2.set_xlabel("*2011 Forecasted Value")

fig.savefig('test.ps')

import iemplot
iemplot.makefeature('test')
