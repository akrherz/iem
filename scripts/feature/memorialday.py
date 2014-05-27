import iemdb
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()
import mx.DateTime

years = []
wind = []
highs = []
for yr in range(1971,2015):
    may31 = mx.DateTime.DateTime(yr,5,31)
    memorial = may31 + mx.DateTime.RelativeDateTime(weekday=(mx.DateTime.Monday,-1))
    acursor.execute("""
    SELECT avg(sknt), max(tmpf) from t%s WHERE station = 'DSM' and 
    valid BETWEEN '%s 00:00' and '%s 00:00'
    and sknt >= 0
    """ % (yr, memorial.strftime("%Y-%m-%d"), 
    (memorial + mx.DateTime.RelativeDateTime(days=1)).strftime("%Y-%m-%d")))
    row = acursor.fetchone()
    years.append(yr)
    wind.append( row[0] )
    highs.append( row[1] )
    print yr, row
    
import numpy as np
import matplotlib.pyplot as plt

years = np.array( years )

(fig, ax) = plt.subplots(2,1, sharex=True)
rects = ax[0].bar( years - 0.4, highs )
ax[0].set_xlim(1970.5, 2014.5)
ax[0].set_ylim(40,90)
#ax.set_yticks((91,121,152))
#ax.set_yticklabels(('Apr 1', 'May 1', 'Jun 1'))

ax[0].set_ylabel("High Temperature [F]")
#ax.set_xlabel("*2011 Total of 106 hours is the least")
ax[0].grid(True)
#ax.set_ylim(35,75)
ax[0].set_title("Des Moines: 1971-2014 Memorial Days")

rects = ax[1].bar( years - 0.4, wind )
ax[1].set_xlim(1970.5, 2014.5)
ax[1].set_ylabel("Average Wind Speed [kts]")
ax[1].grid(True)

fig.savefig('test.ps')

import iemplot
iemplot.makefeature('test')