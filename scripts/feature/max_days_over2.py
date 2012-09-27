import iemdb, iemplot
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
import numpy

data = numpy.zeros( (2013-1880,56), 'f')

for thres in range(50,106):
    ccursor.execute("""
    select year, count(*) from alldata_ia where station = 'IA2203' 
    and high >= %s and year > 1879 and sday < '0912' GROUP by year 
    """ % (thres,))
    for row in ccursor:
        data[row[0]-1893,thres-50] = row[1]
    

import matplotlib.pyplot as plt
(fig, ax) = plt.subplots(1,1)

cfg = {
       2012: {'c': '#FF0000', 'z': 3}, 
       1936: {'c': '#0000FF', 'z': 3}, 
       1934: {'c': '#FF00FF', 'z': 3}, 
       1931: {'c': '#000000', 'z': 3}, 
       }

for yr in range(1880,2013):
    ax.plot(numpy.arange(50,106), data[yr-1893,:], 
            color=cfg.get(yr, {'c':'#bceebc'}).get('c'), 
            zorder=cfg.get(yr, {'z': 1}).get('z'),
            label=cfg.get(yr, {'l': None}).get('l', `yr`),
            linewidth=cfg.get(yr, {'z': 1}).get('z'))

#ax.set_ylim(49,106)
#ax.set_xlim(0,360)
ax.set_ylabel("Days per Year")
ax.set_xlabel("Daily High Temperature $^{\circ}\mathrm{F}$")
ax.set_title("1 Jan - 11 Sep: Des Moines Maximum Number of Days\nAt or Above given High Temperature (1880-2012)")
ax.legend()
ax.grid()

fig.savefig('test.ps')
iemplot.makefeature('test')
