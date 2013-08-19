import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
SELECT day, precip from alldata_ia where stationid = 'ia0200' ORDER by day ASC
""")

import numpy
import mx.DateTime
cnts = numpy.zeros( (366,))
tots = numpy.zeros( (366,))

running = 0
for row in ccursor:
    day = mx.DateTime.DateTime(row[0].year, row[0].month, row[0].day)
    tots[int(day.strftime('%j'))-1] += 1
    if row[1] <= 0.01:
        running += 1
        continue
    if running >= 7:
        for i in range(0 - running, 0):
            cnts[ int((day + mx.DateTime.RelativeDateTime(days=i)).strftime('%j'))-1] += 1
    running = 0
    
import matplotlib.pyplot as plt

fig = plt.figure()
ax= fig.add_subplot(111)

ax.bar( numpy.arange(1,367), cnts / tots * 100., fc='r', ec='r')
ax.grid(True)
ax.set_title("Frequency of a day being part of 7+ dry days\nDaily data from Ames 1893-2011")
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlim(1,367)
ax.set_ylabel("Frequency [%]")

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')