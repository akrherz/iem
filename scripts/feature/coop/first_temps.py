import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

doy = []
d2014 = []

for high in range(32,96):
    ccursor.execute("""
    SELECT avg(m), max(case when year = 2014 then m else null end) from 
    (SELECT year, min(extract(doy from day)) as m from alldata_ia
    where station = 'IA2203' and high >= %s GROUP by year) as foo 
    """ , (high,))
    row = ccursor.fetchone()
    d2014.append( row[1] )
    doy.append(row[0] )
    
import matplotlib.pyplot as plt
import numpy as np
fig = plt.figure()
ax = fig.add_subplot(111)

ax.plot(doy, np.arange(32,96), lw=3, label="Average")
ax.plot(d2014, np.arange(32,96), lw=3, label="2014")
ax.set_xticks( (1,32,60,91,121,152, 182) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun', 'Jul') )
ax.set_xlabel("* thru 7 May 2014")
ax.grid(True)
ax.legend(loc=2)
ax.set_ylabel("Temperature ${^\circ}$F")
ax.set_title("First Temperature Exceedance after 1 Jan\n Des Moines [1886-2013]")
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
