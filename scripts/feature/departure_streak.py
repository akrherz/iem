import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
 SELECT day, ((o.high + o.low)/2.0) - ((c.high + c.low)/2.0) from 
 alldata_ia o JOIN climate81 c on (to_char(c.valid, 'mmdd') = o.sday
 and c.station = o.station) WHERE o.station = 'IA2203' and day >= '2012-01-01'
 ORDER by day ASC 


""")

diff = []
days = []
for row in ccursor:
    diff.append( row[1] )
    days.append( row[0] )

import matplotlib.pyplot as plt
fig = plt.figure()
ax= fig.add_subplot(111)

bars = ax.bar(days, diff,fc='r', ec='r')
for i in range(len(diff)):
    if diff[i] < 0:
        bars[i].set_facecolor('b')
        bars[i].set_edgecolor('b')
ax.grid(True)
ax.set_ylabel("Temperature Departure $^{\circ}\mathrm{F}$")
ax.set_title("1 Jan 2012 - 25 Feb 2013 Des Moines\nDaily Average (high+low)/2 Temperature Departure")
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
