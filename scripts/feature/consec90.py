#!/mesonet/python/bin/python
import mx.DateTime
import sys
import numpy
import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()


ccursor.execute("""SELECT year, day, high, low, precip from alldata_ia 
  WHERe station = 'IA2203' and day > '1880-01-01'
  ORDER by day ASC""")

running = 0
biggest = numpy.zeros( (2013-1880), 'f')
for row in ccursor:
  yr = int(row[0])
  if row[2] < 97:
    if running > biggest[yr-1880]:
      biggest[yr-1880] = running
    running = 0
  else:
    running += 1
#biggest[2012-1880] += 1


import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)

bars = ax.bar(numpy.arange(1880,2013) - 0.5, biggest , fc='r', ec='r')
bars[-1].set_facecolor('b')
bars[-1].set_edgecolor('b')
ax.set_xlim(1879.5,2013.5)
ax.set_ylabel("Consecuative Days")
ax.set_title("Des Moines Consecuative Days with highs at or above 97$^{\circ}\mathrm{F}$\nMaximum by year [1880-2012]")
ax.set_xlabel("*2012 Total thru 2 July", color='b')
ax.grid(True)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')

