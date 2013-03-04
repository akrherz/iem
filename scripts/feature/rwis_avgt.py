import iemdb
import numpy

RWIS = iemdb.connect('rwis', bypass=True)
rcursor = RWIS.cursor()

rcursor.execute("""
 select extract(doy from valid) as d, avg(tfs1), stddev(tfs1),
 sum(case when tfs1 < 32 then 1 else 0 end), count(*) from alldata 
 where station = 'RMTI4' and extract(hour from valid) between 12 and 16 
 and tfs1 between -30 and 160 
 GROUP by d ORDER by d ASC
  """)
doy = []
avg = []
stddev = []
freq = []
for row in rcursor:
    doy.append( row[0] )
    avg.append( row[1] )
    stddev.append( row[2] )
    freq.append( row[3] / float(row[4]) * 100.0 )

def movingaverage(interval, window_size):
    window = numpy.ones(int(window_size))/float(window_size)
    return numpy.convolve(interval, window, 'same')

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

ax.plot(doy, avg, label='Average')
ax2 = ax.twinx()
ax2.plot(doy, freq, color='r', label='Frequency')
ax2.set_ylabel("Frequency of Freezing Temperature [%]", color='r')
ax2.set_ylim(0,100)
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlim(1,366)
ax.plot([1,366], [32,32], linestyle='--')
#ax.plot(doy, stddev, label='Pavement')
ax.grid(True)
ax.set_title("2000-2012 Marshalltown RWIS US-30\nAverage Noon-4 PM Pavement Temperature")
ax.set_ylabel('Average Temperature $^{\circ}\mathrm{F}$', color='b')

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
