import datetime
import os
import numpy
import matplotlib.pyplot as plt

d0 = []
d1 = []
d2 = []
d3 = []
d4 = []

for yr in range(2000,2014):
   hit = False
   for dy in range(30,20, -1):
       fn = "/mesonet/data/dm/text/%s04%s.dat" % (yr, dy)
       if not os.path.isfile(fn) or hit:
           continue
       for line in open(fn):
           tokens = line.split(",")
           if tokens[1] == 'IA':
               d0.append( float(tokens[3]) )
               d1.append( float(tokens[4]) )
               d2.append( float(tokens[5]) )
               d3.append( float(tokens[6]) )
               d4.append( float(tokens[7]) )
               hit = True

d0 = numpy.array(d0)
d1 = numpy.array(d1)
d2 = numpy.array(d2)
d3 = numpy.array(d3)
d4 = numpy.array(d4)
print d3
(fig, ax) = plt.subplots(1,1)

ax.bar(numpy.arange(2000,2014)-0.4, d0, zorder=1, fc='#f6eb13', ec='#f6eb13', label='D0 Abnormal')
ax.bar(numpy.arange(2000,2014)-0.4, d1, zorder=2, fc='#ffcc66', ec='#ffcc66', label='D1 Moderate')
ax.bar(numpy.arange(2000,2014)-0.4, d2, zorder=2, fc='#ff9900', ec='#ff9900', label='D2 Severe')
ax.bar(numpy.arange(2000,2014)-0.4, d3, zorder=2, fc='#ff3333', ec='#ff3333', label='D3 Extreme')
ax.bar(numpy.arange(2000,2014)-0.4, d4, zorder=2, fc='#FF00FF', ec='#FF00FF', label='D4 Exceptional')

ax.set_title("Iowa Drought Coverage on Last Week of April")
ax.set_ylabel("Areal Coverage [%]")
ax.set_xlim(1999.5,2013.5)
ax.set_xlabel("based on weekly US Drought Monitor")
ax.grid(True)
ax.legend(ncol=2, fontsize=12)
ax.set_yticks([0,25,50,75,100])

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
