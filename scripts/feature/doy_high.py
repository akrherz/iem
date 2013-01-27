import iemdb
coop = iemdb.connect('asos', bypass=True)
ccursor = coop.cursor()
import numpy as np
import datetime

ccursor.execute("""
 select extract(doy from twelve.d) as doy, 
 sum(case when six.avg > twelve.avg then 1 else 0 end), count(*),
 max(six.avg - twelve.avg) 
 from (select date(valid) as d, avg(tmpf) from alldata where station = 'DSM' 
       and extract(hour from valid + '10 minutes'::interval) = 12 and 
       tmpf is not null GROUP by d) as twelve, 
      (select date(valid) as d, avg(tmpf) from alldata where station = 'DSM'
       and extract(hour from valid + '10 minutes'::interval) = 6 and 
       tmpf is not null GROUP by d) as six 
 WHERE six.d = twelve.d GROUP by doy ORDER by doy ASC
""")
freq = []
doy = []
maxv = []
for row in ccursor:
    doy.append( datetime.datetime(2000,1,1) + datetime.timedelta(days=int(row[0]-1)))
    freq.append( float(row[1]) / float(row[2]) * 100.0)
    maxv.append( float(row[3]) )

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

(fig, ax) = plt.subplots(2,1, sharex=True)

ax[0].bar(doy, freq, fc='purple', ec='purple')
bars = ax[1].bar(doy, maxv, fc='blue', ec='blue')
for i in range(len(maxv)):
    if maxv[i] < 0:
        bars[i].set_facecolor('r')
        bars[i].set_edgecolor('r')

ax[0].set_title("Des Moines [1933-2012] Noon Temperature colder than 6 AM")
ax[0].set_ylabel("Frequency [%]")
ax[1].set_ylabel("Largest Difference $^{\circ}\mathrm{F}$")
#ax.set_xlabel("[1893-2010]")
#ax.set_xlim(90,305)
ax[0].grid(True)
ax[1].grid(True)
ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%b'))

fig.tight_layout()

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
