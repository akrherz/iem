import datetime
import sys
import numpy as np
import iemdb
COOP = iemdb.connect("coop", bypass=True)
ccursor = COOP.cursor()


ccursor.execute("""SELECT day, precip from alldata_ia 
  WHERe station = 'IA2203' and month in (5,6,7,8) and year > 1879
  ORDER by day ASC"""  )

years = []
vals = []
running = 0
biggest = 0
for row in ccursor:
    if row[0].month == 5 and row[0].day == 1:
        running = 0
        biggest = 0
        years.append(row[0].year)
    if row[1] < 0.1:
        running += 1
    else:
        running = 0
    if running > biggest:
        biggest = running
    if row[0].month == 8 and row[0].day == 31:
        vals.append( biggest )

vals.append( biggest )
vals = np.array(vals)

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)

avgv = np.average(vals)
bars = ax.bar(np.array(years)-0.4, vals , fc='r', ec='r')
bars[-1].set_facecolor('g')
bars[-1].set_edgecolor('g')
for i, bar in enumerate(bars):
    if bar.get_height() > 27:
        ax.text(bar.get_x(), bar.get_height(), "%s" % (years[i],))
ax.plot([1879,2013.5], [avgv, avgv], c='k', lw=2)

ax.set_ylim(top=46)
ax.set_xlim(1879,2014)
ax.set_ylabel("Longest Period [days]")
ax.set_title("Des Moines [1 May - 31 Aug] Consec Days Below 0.10\" Precip")
ax.set_xlabel("*2013 (green bar) Total thru 21 Jul, average %.1f days" % (avgv,))
ax.grid(True)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')

