import iemdb
import numpy
from numpy.random import rand
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""SELECT day, high from alldata_ia where station = 'IA2203'
  and month = 7 ORDER by day ASC""")
records = [-99]*31
counts = [0]*31

bars = [{'year': 1800, 'highs': [], 'days': []}]

for row in ccursor:
  if row[1] > records[ row[0].day - 1]:
    records[ row[0].day - 1 ] = row[1]
    counts[ row[0].day - 1 ] += 1
    if bars[-1]['year'] != row[0].year:
      bars.append( {'year': row[0].year, 'highs': [], 'days': []} )
    bars[-1]['highs'].append( row[1] )
    bars[-1]['days'].append( row[0].day  )

import matplotlib.pyplot as plt
import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=10)

fig = plt.figure()
ax = fig.add_subplot(111)

for i in range(len(bars)-1,-1,-1):
  c = tuple(rand(3))
  if c[0] > 0.9:
    c = tuple(rand(3))
  if bars[i]['year'] == 2012:
    c = [1,0,0]
  if bars[i]['year'] == 1879:
    c = '#EEEEEE'
  if bars[i]['year'] == 1910:
    c = '#00FF00'
  label = None
  if len(bars[i]['days']) > 2:
    label= str(bars[i]['year'])
  ax.bar( numpy.array(bars[i]['days'])-0.4, bars[i]['highs'], 
    label=label, color=c)

for i in range(31):
  ax.text(i+1, records[i]+1, "%s" % (counts[i],), ha='center')

ax.legend(ncol=6,loc=2, prop=prop)
ax.set_ylim(75,120)
ax.set_title("Des Moines Daily High Temperature Records\n1 March 1879 - 20 March 2012")
ax.set_ylabel("Temperature $^{\circ}\mathrm{F}$")
ax.set_xlabel("* Only years with 3+ records set are labeled\n number of times record set is shown above bars")
ax.grid(True)
ax.set_xlim(0.5,31.5)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
