import numpy
import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

y2012 = []
ccursor.execute("""SELECT high from alldata_ia where station = 'IA2203'
 and year = 2012 and sday < '0307' and sday != '0228' ORDER by day ASC""")
for row in ccursor:
    y2012.append( row[0] )
    
y2013 = []
ccursor.execute("""SELECT high from alldata_ia where station = 'IA2203'
 and year = 2013 and sday < '0307' ORDER by day ASC""")
for row in ccursor:
    y2013.append( row[0] )
y2013.append( 33 )
y2012 = numpy.array(y2012)
y2013 = numpy.array(y2013)
diff = y2013 - y2012

import matplotlib.pyplot as plt
(fig, ax) = plt.subplots(1,1)

bars = ax.bar(numpy.arange(1, len(y2012)+1)-0.4, diff, fc='b')
for i in range(len(bars)):
    if diff[i] > 0:
        bars[i].set_facecolor('r')
ax.grid(True)
ax.set_xlim(0,67)
ax.set_xticks([1,32,60])
ax.set_xticklabels(['1 Jan', '1 Feb', '1 Mar'])
ax.set_ylabel("Temperature Difference $^{\circ}\mathrm{F}$")
ax.set_title("Des Moines 2013 vs 2012 Daily High Temperature")

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')