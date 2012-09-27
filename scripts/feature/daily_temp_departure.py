import iemdb
import numpy
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""select day, a.high, c.high, a.low, c.low from alldata_ia a, climate81 c where c.station = a.station and c.station = 'IA2203' and year = 2012 and a.sday = to_char(c.valid, 'mmdd') ORDER by day ASC""")

diff = []
ldiff = []
for row in ccursor:
    diff.append( row[1] - row[2] )
    ldiff.append( row[3] - row[4] )
    
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(2,1, sharex=True)

bars = ax[0].bar(numpy.arange(1,len(diff)+1)-0.5, diff, fc='b', ec='b')
for bar in bars:
    if bar.get_y() == 0:
        bar.set_facecolor('r')
        bar.set_edgecolor('r')
ax[0].grid(True)
ax[0].set_title("1 Jan - 12 Aug 2012 Des Moines Daily Temperature Departure")
ax[0].set_ylabel("High Temperature $^{\circ}\mathrm{F}$")
ax[1].set_ylabel("Low Temperature $^{\circ}\mathrm{F}$")

bars = ax[1].bar(numpy.arange(1,len(diff)+1)-0.5, ldiff, fc='b', ec='b')
for bar in bars:
    if bar.get_y() == 0:
        bar.set_facecolor('r')
        bar.set_edgecolor('r')
ax[1].set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax[1].set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax[1].set_xlim(0,len(diff)+1)
ax[1].grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')