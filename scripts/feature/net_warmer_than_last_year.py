import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
  SELECT extract(year from second.day) as yr, 
  sum(case when second.high > first.high then 1 else 0 end) +
  sum(case when second.high < first.high then -1 else 0 end) from
  (SELECT day, high from alldata_ia where station = 'IA2203' 
  and day >= '1880-01-01' and sday != '0229') as second,
  (SELECT day + '1 year'::interval as d, high from alldata_ia where station = 'IA2203' 
  and day >= '1880-01-01' and sday != '0229') as first WHERE second.day = first.d
  GROUP by yr ORDER by yr ASC
""")

years = []
net = []
for row in ccursor:
    years.append( row[0] )
    net.append( float(row[1]) )
import numpy
years = numpy.array( years )
net = numpy.array( net )

import matplotlib.pyplot as plt
import iemplot
import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=12)

fig, ax = plt.subplots(1,1)
bars = ax.bar( years - 0.4, net, 
        facecolor='purple', ec='purple', zorder=1, label='After 19 Aug')
for bar in bars:
    if bar.get_y() == 0:
        bar.set_facecolor('r')
        bar.set_edgecolor('r')

ax.set_title("Net Days Warmer than a Year Ago\nDes Moines Daily High Temperature (1880-2012)")
ax.grid(True)
ax.set_ylabel('Net Days per Year')
ax.set_xlim(1879.5,2013.5)
ax.set_xlabel("* 2012 thru Oct 25")



fig.savefig('test.ps')
iemplot.makefeature('test')