import iemdb 
import numpy as np
import datetime
import mx.DateTime
ASOS = iemdb.connect('iem', bypass=True)
acursor = ASOS.cursor()

days = []
diff = []
diff2 = []

acursor.execute("""
 select dsm.day, dsm.min_tmpf - ikv.min_tmpf as d , dsm.max_tmpf - ikv.max_tmpf as d2 from 
 (select day, min_tmpf, max_tmpf from summary s JOIN stations t on 
 (t.iemid = s.iemid) WHERE t.id = 'DSM' and day >= '2010-12-14') 
 as dsm JOIN (select day, min_tmpf, max_tmpf from summary s JOIN stations t 
 on (t.iemid = s.iemid) WHERE t.id = 'IKV' and day >= '2010-12-14' and day < '2013-01-03'
 and min_tmpf < 99) 
 as ikv on (ikv.day = dsm.day)  ORDER by dsm.day ASC
  """ )
for row in acursor:
    days.append( row[0] )
    diff.append( row[1] )
    diff2.append( row[2] )

import matplotlib.pyplot as plt
(fig, ax) = plt.subplots(2, 1, sharex=True)

bars = ax[0].bar(days, diff2, fc='b', ec='b')
for i in range(len(bars)):
    if diff2[i] > 0:
        bars[i].set_facecolor('r')
        bars[i].set_edgecolor('r')

ax[0].text( days[10], 7, "Des Moines Warmer", color='r')
ax[0].text( days[10], -7, "Ankeny Warmer", color='b')

bars = ax[1].bar(days, diff, fc='b', ec='b')
for i in range(len(bars)):
    if diff[i] > 0:
        bars[i].set_facecolor('r')
        bars[i].set_edgecolor('r')

ax[1].text( days[10], 11, "Des Moines Warmer", color='r')
ax[1].text( days[10], -7, "Ankeny Warmer", color='b')


ax[0].grid(True)
ax[0].set_ylabel("High Temperature $^{\circ}\mathrm{F}$")
ax[0].set_title("Des Moines [DSM] - Ankeny [IKV] Daily Temperature Difference")

ax[1].grid(True)
ax[1].set_ylabel("Low Temperature $^{\circ}\mathrm{F}$")

fig.tight_layout()
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
