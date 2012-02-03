import iemdb, network
import numpy

COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
 SELECT extract(year from day + '2 months'::interval) as yr, min(low) 
 from alldata_ia where station = 'IA2203' and 
 (month in (11,12) or sday < '0327') GROUP by yr ORDER by yr ASC
""")

data = []
for row in ccursor:
    if row[0] > 1893 and row[0] < 2013:
        data.append( row[1]  )
    
data = numpy.array(data)

import matplotlib.pyplot as plt
import iemplot

fig = plt.figure()
ax = fig.add_subplot(111)

bars = ax.bar( numpy.arange(1894, 2013) - 0.4, data, 
        facecolor='b', ec='b', zorder=1, label="After 17 Jan")
i = 1894
for bar in bars:
    if bar.get_xy()[1] ==  0 and bar.get_height() >= 0:
        bar.set_facecolor('r')
        bar.set_edgecolor('r')
        ax.text(i-0.5, bar.get_height()+3, i, ha='center', rotation=90)
    i += 1
ax.set_ylim(-30,10)
ax.set_xlim(1892.5, 2013)
ax.set_title("Des Moines Minimum Winter Temperature\n1 November 2011 - 26 January [1894-2012]")
ax.grid(True)
#ax.set_ylim(0,100)
#ax.legend(loc=2)
ax.set_ylabel('Minimum Temperature $^{\circ}\mathrm{F}$')
#ax.set_xlabel("* 212 ties the latest date to have a sub-zero temp")
fig.savefig('test.ps')
iemplot.makefeature('test')
