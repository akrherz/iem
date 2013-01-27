import iemdb
import numpy
import matplotlib.pyplot as plt
(fig,ax) = plt.subplots(1,1)
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

cnt = 0.0
total = numpy.zeros(33)

for year in range(1893,2012):
    ccursor.execute(""" SELECT high from alldata_ia where station = 'IA0200'
    and day >= '%s-09-01' and day < '%s-05-01' ORDER by day ASC""" % (
                                                        year, year+1))
    highs = []
    for row in ccursor:
        highs.append( row[0])
    highs = numpy.array( highs )

    maxes = numpy.zeros(33)
    
    for i in range(len(highs)-1):
        for j in range(i+1,len(highs)):
            days = j-i
            maxv = int( max(0, numpy.max( highs[i:j])) )
            if maxv > 32:
                continue
            for idx in range(maxv, 33):
                if maxes[idx] < days:
                    maxes[idx] = days
                   
    if maxes[-1] > 32:
        print year, maxes 
        ax.plot(numpy.arange(0,33),maxes, label="%s-%s"%(year,year+1,), zorder=2)
    else:
        ax.plot(numpy.arange(0,33),maxes, color='tan', zorder=1)
    
    total += maxes
    cnt += 1.0

ax.plot(numpy.arange(0,33), total / cnt, label='Average', color='k', zorder=3,
        linewidth=2.0)
ax.set_title("Ames Winter Consecutive Days Below Temperature [1893-2012]")
ax.set_ylabel("Consecutive Days")
ax.set_xlabel("Temperature Threshold $^{\circ}\mathrm{F}$")
ax.set_xlim(0,32)
ax.grid(True)
ax.legend(loc=2, ncol=2)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test') 