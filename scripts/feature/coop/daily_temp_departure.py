import iemdb
import numpy
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

def get_year(yr):
    ccursor.execute("""select day, a.high, c.high, a.low, c.low from alldata_ia a, 
        climate81 c where c.station = a.station and c.station = 'IA2203' and 
        year = %s and a.sday = to_char(c.valid, 'mmdd') ORDER by day ASC""",
        (yr,))

    diff = []
    ldiff = []
    for row in ccursor:
        diff.append( row[1] - row[2] )
        ldiff.append( row[3] - row[4] )
    
    return diff, ldiff
    
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(3,1, sharex=True)

diff, ldiff = get_year(2012)
bars = ax[0].bar(numpy.arange(1,len(diff)+1)-0.5, diff, fc='b', ec='b')
for bar in bars:
    if bar.get_y() == 0:
        bar.set_facecolor('r')
        bar.set_edgecolor('r')
ax[0].grid(True)
ax[0].set_title("Des Moines Daily High Temperature Departure")
ax[0].set_ylabel("2012 Departure $^{\circ}\mathrm{F}$")
ax[1].set_ylabel("1988 Departure $^{\circ}\mathrm{F}$")
ax[2].set_ylabel("1934 Departure $^{\circ}\mathrm{F}$")
ax[0].set_ylim(-40,40)

diff, ldiff = get_year(1988)
bars = ax[1].bar(numpy.arange(1,len(diff)+1)-0.5, diff, fc='b', ec='b')
for bar in bars:
    if bar.get_y() == 0:
        bar.set_facecolor('r')
        bar.set_edgecolor('r')
ax[1].set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax[1].set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax[1].set_xlim(0,len(diff)+1)
ax[1].set_ylim(-40,40)
ax[1].grid(True)

diff, ldiff = get_year(1934)
bars = ax[2].bar(numpy.arange(1,len(diff)+1)-0.5, diff, fc='b', ec='b')
for bar in bars:
    if bar.get_y() == 0:
        bar.set_facecolor('r')
        bar.set_edgecolor('r')
ax[2].set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax[2].set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax[2].set_xlim(0,len(diff)+1)
ax[2].grid(True)
ax[2].set_ylim(-40,40)

fig.savefig('test.png')
#import iemplot
#iemplot.makefeature('test')