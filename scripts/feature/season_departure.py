import iemdb
import numpy
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

# load up climatology
normal = []
running = 0
ccursor.execute("""SELECT valid, precip from climate where station = 'ia0200' and valid >= '2000-05-01' ORDER by valid ASC""")
for row in ccursor:
  running += row[1]
  normal.append( running )

largest = numpy.zeros( (2012-1893) )
smallest = numpy.zeros( (2012-1893) )
for yr in range(1893,2012):
  ccursor.execute("""SELECT day, precip, month from alldata_ia where stationid = 'ia0200' and month in (5,6,7,8) and year = %s ORDER by day ASC""", (yr,))
  running = 0
  i = 0
  for row in ccursor:
    running += row[1]
    diff = running - normal[i]
    if diff > largest[yr-1893] and row[2] == 8:
      largest[yr-1893] = diff
    elif diff < smallest[yr-1893] and row[2] == 8:
      smallest[yr-1893] = diff
    i += 1

import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111)
ax.bar(numpy.arange(1893,2012)-0.4, largest, fc='b', ec='b', label='Wettest')
ax.bar(numpy.arange(1893,2012)-0.4, smallest, fc='r', ec='r', label='Driest')
ax.set_xlim(1892.5, 2011.5)
ax.grid(True)
ax.set_title("Largest August Precipitation Departure since 1 May\nFor Ames versus Long Term Average by Year")
ax.set_ylabel("Precipitation Departure [inches]")

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
