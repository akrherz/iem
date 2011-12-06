import iemdb
import numpy
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
 SELECT day + '4 months'::interval, day, high from alldata_ia where station = 'IA0200' 
 and day > '1899-09-01' ORDER by day ASC
""")

doy = []
cnts = []
ryear = 1900
mindoy = None
for row in ccursor:
    if mindoy is None and row[2] < 32:
        ryear = row[0].year
        mindoy = 1
        doy.append( int(row[0].strftime("%j")) )
        cnts.append( 0 )
    if row[2] < 32:
        cnts[-1] += 1
    if ryear != row[0].year:
        mindoy = None
        ryear = row[0].year

import matplotlib.pyplot as plt
import mx.DateTime
cnts = numpy.array(cnts)

xticks = [1,32,62,93,124]
xticklabels = ['1 Sep','1 Oct', '1 Nov', '1 Dec', '1 Jan']

fig = plt.figure()
ax = fig.add_subplot(311)
ax.scatter( numpy.arange(1899,2012), doy)
ax.set_yticks(xticks)
ax.set_yticklabels(xticklabels)
ax.set_ylim(32,135)
ax.set_xlim(1898.5,2011.5)
ax.set_ylabel("First Day")
ax.grid(True)
ax.set_title("Ames [1900-2011] Days Below Freezing")

ax2 = fig.add_subplot(312)
bars = ax2.bar( numpy.arange(1899,2011)-0.4, cnts[:-1], facecolor='b', 
        edgecolor='b')
avgV = numpy.average(cnts)
for bar in bars:
  if bar.get_height() < avgV:
    bar.set_facecolor('r')
    bar.set_edgecolor('r')
ax2.set_xlim(1898.5,2010.5)
ax2.set_ylabel("Frozen Days")
ax2.grid(True)

ax3 = fig.add_subplot(313)
ax3.scatter( doy[:-1], cnts[:-1], color='b')
ax3.set_xticks(xticks)
ax3.set_xticklabels(xticklabels)
ax3.set_xlim(32,135)
ax3.plot([32,135], [avgV,avgV], color='k')
ax3.grid(True)     
ax3.set_xlabel("First Day")
ax3.set_ylabel("Frozen Days")


fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
