import iemdb
coop = iemdb.connect('coop', bypass=True)
ccursor = coop.cursor()
import numpy as np
import mx.DateTime

def fetch(station):
    doy = []
    for low in range(40,-10,-1):
        ccursor.execute("""
    select avg(min) from (select extract(year from d) as yr, min(extract(doy from d)) 
    from (select day + '4 months'::interval as d, low from alldata_ia where station = %s) 
    as foo WHERE low < %s GROUp by yr) as foo2
        """, (station, low))
        row = ccursor.fetchone()
        doy.append( row[0] )
    return doy

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)

ax.plot(fetch('IA2203'), np.arange(40,-10,-1), label='Des Moines', linewidth=2 )
ax.plot(fetch('IA0200'), np.arange(40,-10,-1), label='Ames' , linewidth=2)
ax.plot(fetch('IA4705'), np.arange(40,-10,-1), label='Davenport', linewidth=2 )
ax.plot(fetch('IA7708'), np.arange(40,-10,-1), label='Sioux City', linewidth=2 )
sts = mx.DateTime.DateTime(2000,9,1)
ets = mx.DateTime.DateTime(2001,2,1)
interval = mx.DateTime.RelativeDateTime(months=1)
now = sts
xticks = []
xticklabels = []
while now < ets:
  xticks.append( (now - sts).days )
  xticklabels.append( now.strftime("%b %-d") )
  now += interval 
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)
ax.set_title("Average Date of First Fall Temperature below...")
ax.set_ylabel("Low Temperature $^{\circ}\mathrm{F}$")
#ax.set_xlabel("[1893-2010]")
#ax.set_xlim(90,305)
ax.legend()
ax.grid(True)


fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
