import iemdb
import numpy
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("SELECT day, high, extract(doy from day) from alldata WHERE stationid = 'ia0200' and year > 1893 and year < 2011 ORDER by day ASC")

dchange = numpy.zeros( (366,))
uchange = numpy.zeros( (366,))

lval = 0
for row in ccursor:
    diff = lval - row[1]
    if diff < dchange[row[2]-1]:
        dchange[row[2]-1] = diff
    if diff > uchange[row[2]-1]:
        uchange[row[2]-1] = diff
    lval = row[1]
            
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)
ax.bar( numpy.arange(1,367) - 0.4, dchange, facecolor='b', edgecolor='b')
ax.bar( numpy.arange(1,367) - 0.4, uchange, facecolor='r', edgecolor='r')

#ax.text(maxB[0,-1], maxB[1,-1], ' 2010 Mar 2 [%.0f,%.0f]' % (maxB[0,-1], maxB[1,-1]))

ax.set_xlim(0.5,367.5)
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
#ax.set_ylim(0,100)
ax.set_ylabel("High Temperature Change [F]")
#ax.set_xlabel(" [days]")
#ax.set_xticks( [1,3,5,7,9,11] )
#ax.set_xticklabels( ['Jan','Mar','May','Jul','Sep','Nov'] )

ax.set_title("Extreme Day to Day High Temperature Change\nAmes [1893-2010]")
ax.grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
