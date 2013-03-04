import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
import numpy

increase = numpy.zeros( (12,))
nochange = numpy.zeros( (12,))
decrease = numpy.zeros( (12,))

ccursor.execute("""SELECT day, high from alldata_ia where
  station = 'IA0200' ORDER by day ASC""")

last = 0
for row in ccursor:
    if row[1] > last:
        increase[ row[0].month -1 ] += 1.0
    elif row[1] < last:
        decrease[ row[0].month -1 ] += 1.0
    elif row[1] == last:
        nochange[ row[0].month -1 ] += 1.0
    last = row[1]

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

total = decrease + nochange + increase

ax.bar( numpy.arange(1,13)-0.4, decrease / total * 100.0, fc='b', label='Decrease')
ax.bar( numpy.arange(1,13)-0.4, nochange / total * 100.0, bottom=(decrease/total * 100.0), fc='g', label="No Change")
ax.bar( numpy.arange(1,13)-0.4, increase / total * 100.0, bottom=(decrease+nochange)/total * 100.0,  fc='r', label="Increase")

for i in range(1,13):
    ax.text(i, decrease[i-1] / total[i-1] * 100.0 - 5, "%.0f" % (
	decrease[i-1] / total[i-1] * 100.0), ha='center')
    ax.text(i, decrease[i-1] / total[i-1] * 100.0 + 2, "%.0f" % (
	nochange[i-1] / total[i-1] * 100.0), ha='center')
    ax.text(i, (decrease[i-1] + nochange[i-1])/ total[i-1] * 100.0 + 2, "%.0f" % (
	increase[i-1] / total[i-1] * 100.0), ha='center')

ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xticks( numpy.arange(1,13))
ax.legend(ncol=3)
ax.set_xlim(0.5,12.5)
ax.set_ylabel("Percentage of Days [%]")
ax.set_title("Ames 1893-2012 Day to Day High Temperature Change")
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
