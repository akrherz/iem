import matplotlib.pyplot as plt
import matplotlib.font_manager 
import numpy
prop = matplotlib.font_manager.FontProperties(size=10) 
from pyIEM import mesonet
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_xlim(0,1443)
xticks = []
xticklabels = []
for x in range(0,25,2):
    xticks.append( x * 60 )
    if x == 0 or x == 24:
        lbl = 'Mid'
    elif x == 12:
        lbl = 'Noon'
    else:
        lbl = x % 12
    xticklabels.append(lbl)
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)
#ax.set_xlabel("Local Hour of Day [CDT]")
#ax.set_ylabel("Air & Dew Point (dash) Temp [F]", fontsize=9)
ax.set_title("7 March 2012 Cold Front Passage")
ax.set_ylabel("Air Temperature $^{\circ}\mathrm{F}$")
ax.set_xlabel("CST")
ax.set_ylim(30,75)

import iemdb
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

names = {'CBF': 'Council Bluffs', 'AXA': 'Algona', 'SHL': 'Sheldon',
   'TNU': 'Newton', 'AWG': 'Washington', 'DEH': 'Decorah',
   'BNW': 'Boone'}

for id in ['CBF', 'AXA','SHL','BNW','TNU','AWG','DEH']:
    icursor.execute("""
        SELECT valid, tmpf from current_log c JOIN stations s on (s.iemid = c.iemid)
        where valid > '2012-03-07' and valid < '2012-03-08' and s.id = '%s' ORDER by valid ASC
        """ % (id,))
    times = []
    tmpf = []
    for row2 in icursor:
        times.append( row2[0].hour * 60 + row2[0].minute )
        tmpf.append( row2[1] )
    tmpf = numpy.array( tmpf )
    ax.plot(times, tmpf, label='%s'% (names[id],))
ax.grid(True)
ax.legend(loc=2, ncol=4, prop=prop)

import iemplot
fig.savefig('test.ps')

iemplot.makefeature('test')
