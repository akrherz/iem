import psycopg2
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()

cnt2012 = []
cnt2013 = []
avgs = []

for t in [50,60,70,80,90]:
    cursor.execute("""SELECT year, count(*) from alldata_ia WHERE
        station = 'IA0200' and high between %s and %s 
        and sday < '0605' GROUP by year
        """, (t, t+10))
    cnts = []
    for row in cursor:
        if row[0] == 2012:
            cnt2012.append( row[1] )
        if row[0] == 2013:
            cnt2013.append( row[1] )
        cnts.append( row[1] )
    avgs.append( sum(cnts) / float(len(cnts)) )

import matplotlib.pyplot as plt
import numpy
(fig, ax) = plt.subplots(1,1)

bars = ax.bar( numpy.arange(5) - 0.45, avgs, width=0.3, fc='g',
        label='Average')
for bar in bars:
    ax.text(bar.get_x() + 0.15, bar.get_height() + 0.5, 
            "%.1f" % (bar.get_height(),), ha='center')
bars = ax.bar( numpy.arange(5) - 0.15, cnt2012, width=0.3, fc='r',
         label='2012')
for bar in bars:
    ax.text(bar.get_x() + 0.15, bar.get_height() + 0.5, 
            "%.0f" % (bar.get_height(),), ha='center')
bars = ax.bar( numpy.arange(5) + 0.15, cnt2013, width=0.3, fc='b',
         label='2013')
for bar in bars:
    ax.text(bar.get_x() + 0.15, bar.get_height() + 0.5, 
            "%.0f" % (bar.get_height(),), ha='center')

ax.set_xlim(-0.5, 4.5)
ax.set_xticks( range(5) )
ax.set_xticklabels( ['50s', '60s', '70s', '80s', '90s'])
ax.set_title("1 Jan - 4 Jun 1893-2013 Ames Daily High Temperature")
ax.set_ylabel("Days")
ax.legend(ncol=3)
ax.set_ylim(0,40)
ax.set_xlabel("High Temperature Ranges")
fig.savefig('test.svg')
import iemplot
iemplot.makefeature('test')
