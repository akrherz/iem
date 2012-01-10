# Month percentile 

import sys, os, random
import iemdb
import iemplot

import mx.DateTime
now = mx.DateTime.now()

COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
ccursor2 = COOP.cursor()

pranks = []
ccursor.execute("""
    SELECT month, sum(precip) from alldata_ia where station = 'IA0200'
    and year = 2011 GROUP by month ORDER by month ASC
""")
for row in ccursor:
    precip = row[1]
    ccursor2.execute("""
    SELECT count(*) from 
    (SELECT year, sum(precip) as s from alldata_ia where station = 'IA0200'
    and month = %s and year < 2011 GROUP by year) as foo where s < %s
    """, (row[0], precip,))
    row2 = ccursor2.fetchone()
    print row[0], precip, row2[0]
    pranks.append( row2[0] / 119.0 * 100.)

print pranks
ames = [49.579831932773111, 74.789915966386559, 25.210084033613445, 67.226890756302524, 72.268907563025209, 72.268907563025209, 45.378151260504204, 40.336134453781511, 20.168067226890756, 21.008403361344538, 90.756302521008408, 91.596638655462186,
         63.0252]
iowa = [22.689075630252102, 42.857142857142854, 26.05042016806723, 56.30252100840336, 
        66.386554621848731, 83.193277310924373, 42.857142857142854, 36.134453781512605, 
        8.4033613445378155, 12.605042016806722, 66.386554621848731, 89.915966386554629,
        73.94957983193278]

iowaT = [25.210084033613445, 48.739495798319325, 54.621848739495796, 41.17647058823529, 
        55.462184873949582, 63.865546218487388, 94.117647058823522, 59.663865546218489, 
        10.084033613445378, 73.109243697478988, 72.268907563025209, 89.075630252100851,
        73.94957983193278]
amesT = [24.369747899159663, 58.82352941176471, 53.781512605042018, 36.97478991596639, 
         47.058823529411761, 58.82352941176471, 93.277310924369743, 47.899159663865547, 
         10.084033613445378, 59.663865546218489, 65.546218487394952, 88.235294117647058,
        49.579]


import numpy
import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(211)

rects = ax.bar( numpy.arange(1,14) - 0.3, iowa, width=0.3, fc='r', label='Iowa')
rects[-1].set_facecolor('#FF969C')
rects2 = ax.bar( numpy.arange(1,14), ames, width=0.3, fc='b', label='Ames')
rects2[-1].set_facecolor('#96A3FF')

#ax.legend(loc=2)
ax.grid(True)
ax.set_yticks( (0,25,50,75,90,95,100))
ax.set_xticks( range(1,14) )
ax.set_xlim(0.6,13.6)
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec', 'Year') )
ax.set_ylabel('Precip Percentile [100=wet]')
ax.set_title("2011 Monthly Precip and Average Temps\nIEM Computed [1893-2011]")

ax = fig.add_subplot(212)

rects = ax.bar( numpy.arange(1,14) - 0.3, iowaT, width=0.3, fc='r', label='Iowa')
rects[-1].set_facecolor('#FF969C')
rects2 = ax.bar( numpy.arange(1,14), amesT, width=0.3, fc='b', label='Ames')
rects2[-1].set_facecolor('#96A3FF')

ax.legend(loc=(0.53,-0.25), ncol=2)
ax.grid(True)
ax.set_yticks( (0,25,50,75,90,95,100))
ax.set_xticks( range(1,14) )
ax.set_ylabel('Temp Percentile [100=warm]')
ax.set_xlim(0.6,13.6)
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec', 'Year') )


fig.savefig('test.ps')
iemplot.makefeature('test')
