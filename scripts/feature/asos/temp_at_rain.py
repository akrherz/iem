import iemdb
import numpy as np
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

acursor.execute("""
    SELECT tmpf, extract(week from valid), p01i, valid from alldata 
    where station = 'DSM' 
    and p01i >= 0.01 and tmpf > -50 and valid < '2013-01-01'
    ORDER by valid ASC
""")

counts = np.zeros( (53,), 'f')
hits = np.zeros( (53,), 'f')

last = None
for row in acursor:
    t = row[3].strftime("%Y%m%d%H")
    if t == last:
        continue
    last = t
    counts[ row[1]-1 ] += 1.0
    if row[0] >= 32:
        hits[ row[1]-1 ] += 1.0
    
print hits
print counts

import iemplot
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.grid(True)
ax.set_ylabel('Frequency above 32$^{\circ}\mathrm{F}$ [%]')
ax.set_title('Frequency of Above Freezing Temp While Reporting Precip\nDes Moines Hourly Data 1933-2012')
ax.bar( np.arange(1,366,7), hits / counts * 100.0, width=7.0, fc='yellow' )
ax.set_yticks([0,25,50,75,100])
ax.set_xlabel("Partitioned by week of the year")
ax.set_xlim(0,371)

fig.savefig('test.ps')
iemplot.makefeature('test')
