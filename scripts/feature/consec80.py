#!/mesonet/python/bin/python
import mx.DateTime
import sys
import numpy
import iemdb
COOP = iemdb.connect("coop", bypass=True)
ccursor = COOP.cursor()


ccursor.execute("""SELECT month, high, year, day from alldata 
  WHERe station = 'IA2203' and day >= '1893-01-01' and month = 12 
  ORDER by day ASC"""  )

running = 0
biggest = 0
for row in ccursor:
  if row[1] >= 50:
    running += 1
    if running >= biggest:
        biggest = running
    if running > 3 and row[3].day > 20:
        print running, row
  else:
    running = 0

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)

bars = ax.bar(numpy.arange(1,13) - 0.4, biggest , fc='r', ec='r')

for i in range(len(bars)):
    bar = bars[i]
    year = years[i]
    if bar.get_height() > 0:
        ax.text(i+1, bar.get_height()+1, "%.0f" % (years[i],),ha='center')
        ax.text(i+1, bar.get_height()- 1.0, "%.0f" % (biggest[i],), ha='center')

ax.set_xlim(0.5,12.5)
ax.set_xticks( numpy.arange(1,13))
ax.set_xticklabels(('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_ylabel("Consecuative Days")
ax.set_title("Ames Consecuative Days with highs over 80$^{\circ}\mathrm{F}$\nMaximum by month, last year occurred [1893-2011]")
ax.set_xlabel("*2011 Total thru 3 Oct")
ax.grid(True)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')

