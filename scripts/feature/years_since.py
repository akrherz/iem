
import pg
import mx.DateTime

conn = pg.connect("coop", "iemdb", user="nobody")

rs = conn.query("SELECT valid, max_high_yr, min_low_yr from climate WHERE station = 'ia0200' and valid != '2000-02-29' ORDER by valid ASC").dictresult()

hyears = []
lyears = []

for row in rs:
  hyears.append( row['max_high_yr'] - 2010 )
  lyears.append( row['min_low_yr'] - 2010 )

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import iemplot

fig = plt.figure()
ax = fig.add_subplot(211)
rects = ax.bar( np.arange(0,365), hyears, color='r')
#ax.set_ylim(0,50)
ax.set_xlim(0,366)
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.grid(True)
#ax.legend()
ax.set_ylabel("Max High Temperature [years]")
ax.set_title("Ames [1893-2010] Years since Record Temperature Set")
ax.set_yticklabels( ('120', '100', '80', '60', '40', '20', '0') )
#ax.text(1941, 22, "Max High Temperature")

ax = fig.add_subplot(212)
rects = ax.bar( np.arange(0,365), lyears, color='b')
#for i in range(len(rects)):
#    if rects[i].get_height() > expect[i]:
#        rects[i].set_facecolor('b')
#ax.plot( np.arange(1893,2011), expect, color='black', label="$365/n$")
#ax.set_ylim(0,50)
ax.set_xlim(0,366)
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_yticklabels( ('120', '100', '80', '60', '40', '20', '0') )
ax.grid(True)
#ax.legend()
ax.set_ylabel("Min Low Temperature $s^{-1}$")
#ax.text(1941, 22, "Min Low Temperature")


fig.savefig("test.png")
#iemplot.makefeature("test")
