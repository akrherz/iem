import iemdb, numpy
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

mindays = numpy.zeros( (63), 'f')
mindays[:] = 300
maxdays = numpy.zeros( (63), 'f')
for yr in range(1890,2012):
    ccursor.execute("""SELECT low from alldata_ia where station = 'IA2203' and 
        day BETWEEN '%s-10-01' and '%s-02-08' and low < 33 
        ORDER by low ASC""" % (yr, yr+1))
    
    days = numpy.zeros( (63), 'f')
    for row in ccursor:
        low = row[0] + 30
        if low < 0:
            low = 0
        for i in range(62,low-1,-1):
            days[i] += 1
    print days, ccursor.rowcount
    if yr == 2010:
        d2011 = days
    if yr < 2011:
        mindays = numpy.where(mindays < days, mindays, days)
        maxdays = numpy.where(days > maxdays, days, maxdays)


import matplotlib.pyplot as plt

fig = plt.figure()

ax = fig.add_subplot(111)
ax.plot( numpy.arange(-30,33), mindays, label="Minimum")
ax.plot( numpy.arange(-30,33), maxdays, label="Maximum")
ax.plot( numpy.arange(-30,33), d2011, label="2010-2011")
ax.plot( numpy.arange(-30,33), days, label="2011-2012")
ax.set_title("Des Moines Days Below Temperature Threshold\n1 October - 8 February [1890-2012]")
ax.set_xlim(-30,32)
ax.grid(True)
ax.set_ylabel("Number of Days")
ax.set_xlabel('Temperature $^{\circ}\mathrm{F}$')
ax.legend(loc=2)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
