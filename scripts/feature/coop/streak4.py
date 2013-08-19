import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
import copy

records = [366]*71 # 30 to 100

for yr in range(1880,2013):
  if yr == 2012:
    records2 = copy.deepcopy(records) 
  ccursor.execute("""SELECT extract(doy from day), high from alldata_ia where station = 'IA2203'
    and year = '%s' and month < 10 ORDER by day ASC""" % (yr,))
  rolling = [-99]*5
  for row in ccursor:
    rolling.pop()
    rolling.insert(0,row[1])
    floor = min(rolling)
    if floor < 30 or floor > 100:
      continue
    doy = row[0]
    while records[floor-30] > doy and floor > 29:
      records[floor-30] = doy
      floor -= 1 

import matplotlib.pyplot as plt
import numpy as np

fig = plt.figure()
ax = fig.add_subplot(111)

ax.plot( np.arange(30,101), records, color='r', drawstyle='steps', label="With 2012")
ax.plot( np.arange(30,101), records2, color='g', drawstyle='steps', label="Prior 2012")
ax.set_yticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_yticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.grid(True)
ax.set_xlim(48,100)
ax.set_ylim(0,244)
ax.legend(loc=2)
ax.set_xlabel("High Temperature Threshold $^{\circ}\mathrm{F}$")
ax.set_ylabel("Earliest Occurrence")
ax.set_title("Des Moines Earliest Four Days above High Temperature\n1880-17 March 2013")


fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
