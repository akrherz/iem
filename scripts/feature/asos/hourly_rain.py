"""
"""
import iemdb
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

climate = []
icursor.execute("""
 select hr, avg(p) from (select extract(year from valid) as yr, 
 extract(hour from valid) as hr, sum(phour) as p from hourly 
 where valid < '2013-01-01' and extract(month from valid) in (6,7,8)
 and extract(doy from valid) < 224 
 and station = 'DSM' GROUP by yr, hr) as foo GROUP by hr ORDER by hr
""")
for row in icursor:
    climate.append( row[1] )

d2012 = []
dhour = []
icursor.execute("""
 select hr, p from (select extract(year from valid) as yr, 
 extract(hour from valid) as hr, sum(phour) as p from hourly_2013
 where  extract(month from valid) in (6,7,8) 
 and station = 'DSM' GROUP by yr, hr) as foo ORDER by hr
""")
for row in icursor:
    dhour.append( row[0] )
    d2012.append( row[1] )
    
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy

(fig, ax) = plt.subplots(1,1)

ax.bar( dhour, d2012, width=0.3, fc='b', ec='b', label='2013: %.2f in' % (sum(d2012),), zorder=2)
ax.bar( numpy.arange(0,24)-0.3, climate, width=0.3, fc='g', ec='g', label='Climate: %.2f in' % (sum(climate),), zorder=2)
#rect = Rectangle((-0.5,0), 8, 0.9, facecolor="#aaaaaa", zorder=1)
#ax.add_patch(rect)
ax.set_xticks( (0,4,8,12,16,20) )
ax.set_xticklabels( ('Mid','4 AM','8 AM', 'Noon', '4 PM', '8 PM') )
ax.set_xlabel("2013 Total")
ax.set_ylabel("Precipitation [inch]")
ax.set_title("Des Moines 1 June - 11 August Hourly Precipitation")
ax.set_xlim(-0.5,23.5)
ax.grid(True)
ax.legend(loc=2)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
