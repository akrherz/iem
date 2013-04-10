import numpy
import matplotlib.pyplot as plt

hi2012 = []
lo2012 = []
hi2013 = []
lo2013 = []
hi_cl = []
lo_cl = []

for line in open('/tmp/ames.txt').readlines()[1:]:
    tokens = line.split(",")
    hi_cl.append( float(tokens[1]))
    lo_cl.append( float(tokens[2]))
    hi2012.append( float(tokens[3]))
    lo2012.append( float(tokens[4]))
    hi2013.append( float(tokens[5]))
    lo2013.append( float(tokens[6]))

hi2012 = numpy.array(hi2012)
lo2012 = numpy.array(lo2012)
hi2013 = numpy.array(hi2013)
lo2013 = numpy.array(lo2013)
hi_cl = numpy.array(hi_cl)
lo_cl = numpy.array(lo_cl)

fig = plt.figure(figsize=(4,4))
ax = fig.add_subplot(111)

ax.bar( numpy.arange(1,32)-0.4, hi2012 - lo2012, bottom=lo2012, zorder=1, 
        fc='r', ec='r', label='2012', alpha=0.5)
ax.bar( numpy.arange(1,32)-0.4, hi2013 - lo2013, bottom=lo2013, zorder=1, 
        fc='b', ec='b', label='2013', alpha=0.5)
ax.plot( numpy.arange(1,32), hi_cl, zorder=3, marker='^', linewidth=2, markersize=7,
         color='k', label="Climate High", linestyle='None')
ax.plot( numpy.arange(1,32), lo_cl, zorder=3, marker='v', linewidth=2, markersize=7,
         color='k', label="Climate Low", linestyle='None')
ax.grid()
ax.set_title("Ames March High + Low Temps")
ax.set_xlabel("Day of March")
ax.set_ylabel("Temperature $^{\circ}\mathrm{F}$")
ax.legend(ncol=2, fontsize=12)
ax.set_xlim(0.5, 31.5)

ax.set_ylim(top=100)
fig.tight_layout()
fig.savefig('test.png')
#iemplot.makefeature('test')
