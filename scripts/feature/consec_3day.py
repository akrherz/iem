import iemdb
import numpy
import datetime
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

maxv = [0]*13
yrs = [0]*13
highs = [0,0,0]
months = [1,1,1]

ccursor.execute("""
SELECT day, high, month from alldata_ia where station = 'IA2203' ORDER by day ASC
""")
for row in ccursor:
  highs.pop()
  highs.insert(0,row[1])
  months.pop()
  months.insert(0,row[2])
  if min(highs) > maxv[ months[0] ]:
    begin = row[0] - datetime.timedelta(days=2)
    print 'New', min(highs), begin
    yrs[begin.month] = begin.year
    maxv[begin.month] = min(highs)

yrs[1] = 2012
maxv[1] = 60

import matplotlib.pyplot as plt
import mx.DateTime
from matplotlib.patches import Rectangle

fig = plt.figure()
ax = fig.add_subplot(111)
bars = ax.bar( numpy.arange(1, 13)-0.4, maxv[1:], fc='r', ec='r')

for i in range(len(bars)):
  ax.text( i+1, bars[i].get_height() + 4, "%s\n%s" % (maxv[i+1],yrs[i+1]),
    ha='center')
  

ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xticks( numpy.arange(1, 13) )
#ax3.plot([32,135], [avgV,avgV], color='k')
ax.grid(True)    
ax.set_ylabel("Temperature $^{\circ}\mathrm{F}$")
ax.set_title("Des Moines Warmest Three Day Period [1888-1 Feb 2012]\n(computed by minimum high temperature for a three day period)")
ax.set_xlabel("Month considered by start of three day period")
ax.set_xlim(0.5, 12.5)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
