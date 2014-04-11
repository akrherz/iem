import numpy as np

data =""" 00 |   647
 01 |   629
 02 |   640
 03 |   655
 04 |   669
 05 |   700
 06 |   695
 07 |   686
 08 |   624
 09 |   591
 10 |   638
 11 |   625
 12 |   609
 13 |   572
 14 |   567
 15 |   572
 16 |   566
 17 |   554
 18 |   574
 19 |   622
 20 |   634
 21 |   640
 22 |   642
 23 |   633"""

data2 = """ 00 |     3
 01 |     2
 02 |     1
 03 |     1
 04 |     2
 05 |     3
 06 |     4
 07 |     2
 08 |     8
 09 |     6
 10 |     7
 11 |     9
 12 |    10
 13 |    12
 14 |    11
 15 |    12
 16 |    11
 17 |    13
 18 |     6
 19 |     3
 20 |     2
 21 |     6
 22 |     3
 23 |     2"""

hrs = []
vals = []
vals2 = []
for line in data.split("\n"):
    tokens = line.split("|")
    hrs.append( float(tokens[0]) )
    vals.append( float(tokens[1]) )
for line in data2.split("\n"):
    tokens = line.split("|")
    vals2.append( float(tokens[1]) )

vals = np.array(vals)
vals2 = np.array(vals2)

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

ax.bar(np.arange(24)-0.4, vals  / np.max(vals), width=0.8, fc='b', ec='b',
 label='All Events, max=%.0f' % (np.max(vals),))
ax.bar(np.arange(24)-0.2, vals2  / np.max(vals2), width=0.4, zorder=2, fc='r', ec='k', label='+SN Reported, max=%.0f' % (np.max(vals2),))
ax.set_xlim(-0.5,23.5)
ax.legend(loc=(0.65,1.01), fontsize=10)
ax.set_xticks(np.arange(0,24,4))
ax.set_xticklabels(("Mid", "4 AM", '8 AM', 'Noon', '4 PM', '8 PM'))
ax.set_xlabel("Central Standard Time")
ax.text(0,1.06, "1973-2013 Des Moines METAR Snow Reports", transform=ax.transAxes)
ax.text(0,1.01, "Hourly Frequency of Snow in Current Weather", transform=ax.transAxes)
ax.set_ylabel("Normalized Frequency")
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
