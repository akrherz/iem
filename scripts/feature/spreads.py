import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""SELECT month, count(*) from alldata_ia where
  station = 'IA7844' and (high - low) < 5 and year > 1950 and year < 2013
  GROUP by month ORDER by month ASC""")

data = []
for row in ccursor:
  data.append( row[1] )

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)
import numpy
data = numpy.array( data )
bars = ax.bar( numpy.arange(1,13)-0.4, data / float(52))
for bar in bars:
  ax.text(bar.get_x() + 0.4, bar.get_height()+0.05, "%.1f" % (bar.get_height(),),
    ha='center')
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xticks( numpy.arange(1,13))
ax.set_title("1951-2012 Spencer Daily High within 4 degrees of Low")
ax.set_ylabel("Average Days Per Month Per Year")
ax.set_ylim(0,1.2)
ax.set_xlim(0.5,12.5)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
