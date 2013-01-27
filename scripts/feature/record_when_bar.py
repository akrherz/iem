import iemdb
import numpy
from numpy.random import rand
COOP = iemdb.connect('coop', bypass=True)
ccursor2 = COOP.cursor()
ccursor = COOP.cursor()

def get_month(month):    
    ccursor.execute("""SELECT day, high from alldata_ia where station = 'IA2203'
      and month = %s ORDER by day ASC""", (month,))
    records = [-99]*31

    deltas = []
    for row in ccursor:
        if row[1] >= records[ row[0].day - 1]:
            records[ row[0].day - 1 ] = row[1]
            if row[0].year < 1929:
                continue
            # Go get day two
            ccursor2.execute("""SELECT high from alldata_ia where
            station = 'IA2203' and day = %s::date + '2 days'::interval""",
            (row[0],))
            row2 = ccursor2.fetchone()
            if row2 is not None:
                deltas.append( float(row2[0]) - row[1] )

    return deltas

data = []
for i in range(1,13):
    data.append( get_month(i) )

import matplotlib.pyplot as plt
import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=10)

fig = plt.figure()
ax = fig.add_subplot(111)

ax.boxplot(data)
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.grid(True, axis='y')
ax.set_ylabel("Day Two High Temperature Change $^{\circ}\mathrm{F}$")
ax.set_title("Des Moines Day Two High Temperature Change\nAfter Daily Record High Set/Tied [1930-2012]")

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
