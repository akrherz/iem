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
        mindoy = 0
        doy.append( int(row[0].strftime("%j")) )
        cnts.append( 0 )
    if row[2] < 32 and mindoy >= 0:
        mindoy += 1
    if row[2] < 32:
        cnts[-1] += 1
    else:
        mindoy = -1
    if ryear != row[0].year:
        first.append( mindoy )
        mindoy = None
        ryear = row[0].year
first.append( mindoy )

import matplotlib.pyplot as plt
import mx.DateTime
cnts = numpy.array(cnts)

xticks = [1,32,62,93,124]
xticklabels = ['1 Sep','1 Oct', '1 Nov', '1 Dec', '1 Jan']

ax3 = fig.add_subplot(111)
ax3.scatter( first, cnts[:-1], color='b')
#ax3.set_xticks(xticks)
#ax3.set_xticklabels(xticklabels)
#ax3.set_xlim(32,135)
#ax3.plot([32,135], [avgV,avgV], color='k')
ax3.grid(True)     
ax3.set_xlabel("First Day")
ax3.set_ylabel("Frozen Days")


fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
