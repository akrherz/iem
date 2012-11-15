import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

for yr in range(1893,2013):
    ccursor.execute("""
    SELECT precip from alldata_ia where station = 'IA0000' and precip > 0
    and year = %s and sday < '1017' ORDER by precip ASC
    """ % (yr,))
    total = 0
    last = 0
    x = []
    y = []
    for row in ccursor:
        if row[0] != last:
           x.append( last )
           y.append( total )
        total += row[0]
        last = row[0]
        
    x.append( last )
    y.append( total )
 
    c = 'tan'
    z = 1
    if yr == 2012:
        c = '#FF0000'
        z = 2
    if yr == 1988:
        c = '#00FF00'
        z = 2
    if yr == 2008:
        c = '#0000FF'
        z = 2
    if yr == 1993:
        c = '#FF00FF'
        z = 2
 
    ax.plot(x, y, color=c, zorder=z)
    if z > 1:
        ax.text(x[-1]+0.02,y[-1], "%s" % (yr,), color=c, va='top')

ax.set_ylabel("Accumulated Precipitation [inch]")
ax.set_xlabel("Daily Precipitation [inch]")
ax.set_title("Yearly Iowa Accumulated Precip by Daily Precip\nstatewide estimate for 1 Jan - 16 Oct [1893-2012]")
ax.grid(True)
    
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')