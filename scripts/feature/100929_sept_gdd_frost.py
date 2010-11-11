import iemdb

COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
SELECT year, sum(gdd50(high,low)), 
sum(case when month in (6,7,8) then precip else 0 end), 
min(low),
min(case when low < 32 and month > 8 then extract(doy from day) else 360 end),
min(case when low < 29 and month > 8 then extract(doy from day) else 360 end)
from alldata where
stationid = 'ia0200' and month in (6,7,8,9,10,11,12) and year < 2010
 GROUP by year ORDER by year ASC
""")

mlow = []
precip = []
gdd = []
doy = []
doy2 = []
marker =[]
colors = []
for row in ccursor:
    gdd.append( row[1])
    mlow.append( row[3] )
    precip.append( row[2] * 2.)
    if row[2] > 18:
        colors.append('r')
        marker.append('+')
    else:
        colors.append('b')
        marker.append('x')
    doy.append( row[4])
    doy2.append( row[5])
    if row[4] < 258:
        print row

import numpy
gdd = numpy.array( gdd , 'f')
doy = numpy.array( doy )
doy2 = numpy.array( doy2 )
mlow = numpy.array( mlow )


import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_xticks( (258,265,274,281, 288, 295, 305, 312, 319) )
ax.set_xticklabels( ('Sep 15', 'Sep 22', 'Oct 1', 'Oct 8', 'Oct 15', 'Oct 22', 'Nov 1', 'Nov 8', 'Nov 15') )
dots = ax.scatter( doy, doy2-doy, c=colors, s=precip)

for x in (258,265,274,281, 288, 295, 305,312, 319):
    ax.plot((x-100,x), (100,0), ':', c=('#000000'))

ax.set_ylim(-1,50)
ax.set_xlim(252,320)

p1 = plt.Rectangle((0, 0), 1, 1, fc="b")
p2 = plt.Rectangle((0, 0), 1, 1, fc="r")
ax.legend((p1, p2), ('JJA Precip < 18"','JJA Precip > 18"'))

ax.set_title("Ames First Fall Temperature Occurence\nDot Size is Jun/Jul/Aug Precip [1893-2009]")
ax.set_ylabel("Days until first sub 29$^{\circ}\mathrm{F}$")
ax.set_xlabel("First day of sub 32$^{\circ}\mathrm{F}$")

ax.grid(True)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')