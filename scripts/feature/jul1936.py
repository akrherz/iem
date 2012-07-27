"""
Can Jul 2012 beat Jul 1936
"""
import numpy
import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

h1936 = []
l1936 = []
ccursor.execute("""
 SELECT high, low from alldata_ia where station = 'IA2203' and month = 7
 and year = 1936 ORDER by day ASC
""")
for row in ccursor:
    h1936.append( row[0] )
    l1936.append( row[1] )
running = numpy.zeros( (31), 'f')
h1936 = numpy.array(h1936)
l1936 = numpy.array(l1936)
for i in range(31):
    running[i] = numpy.average( (h1936[:i+1] + l1936[:i+1]) / 2.0)

h2012 = []
l2012 = []
ccursor.execute("""
 SELECT high, low from alldata_ia where station = 'IA2203' and month = 7
 and year = 2012 ORDER by day ASC
""")
for row in ccursor:
    h2012.append( row[0] )
    l2012.append( row[1] )
h2012.append(105)
l2012.append(81)
# hyp
for h in [99]*6:
    h2012.append( h )
for l in [78]*6:
    l2012.append( l )
    
r2012 = numpy.zeros( (31), 'f')
h2012 = numpy.array(h2012)
l2012 = numpy.array(l2012)
for i in range(31):
    r2012[i] = numpy.average( (h2012[:i+1] + l2012[:i+1]) / 2.0)

import matplotlib.pyplot as plt
import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=12)

(fig, ax) = plt.subplots(1,1)

ax.scatter( range(1,32), h1936, marker='s', zorder=1 , label='1936')
ax.scatter( range(1,32), l1936, marker='s', zorder=1)
ax.plot( range(1,32), running, color='b', label='1936 Avg: %.1f' % (running[-1],))
ax.scatter( range(1,23), h2012[:22], zorder=2, color='r' , label='2012')
ax.scatter( range(1,23), l2012[:22], zorder=2, color='r' )
ax.scatter( range(23,32), h2012[22:], zorder=2, color='g' )
ax.scatter( range(23,32), l2012[22:], zorder=2, color='g' )
ax.plot( range(1,23), r2012[:22], color='r', label='2012 Avg: %.1f' % (r2012[-1],))
ax.plot( range(23,32), r2012[22:], color='g', linestyle='-')
ax.grid(True)
ax.legend(loc=1, ncol=4,prop=prop,columnspacing=1)
ax.set_xlim(0.5, 31.5)
ax.set_title("Can July 2012 beat July 1936 for Des Moines?\nDaily Hi and Lo Temps shown with 98/78 scenario to beat 1936")
ax.set_xlabel("18-31 Jul 2012 are hypothetical")
ax.set_ylabel("Daily Hi/Lo Air Temperature $^{\circ}\mathrm{F}$")
 
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
