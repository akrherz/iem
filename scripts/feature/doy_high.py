import iemdb
coop = iemdb.connect('coop', bypass=True)
ccursor = coop.cursor()
import numpy as np
import mx.DateTime

cnts = np.zeros( (366,) )

for yr in range(1893,2011):
  ccursor.execute("""SELECT extract(doy from day), high from alldata 
    WHERE stationid = 'ia0200' and year = %s ORDER by high DESC LIMIT 7""" %( yr,))
  for row in ccursor:
    cnts[ row[0] - 1] += 1

d2011 = np.zeros( (7,) )
ccursor.execute("""SELECT extract(doy from day), high from alldata 
    WHERE stationid = 'ia0200' and year = 2011 ORDER by high DESC LIMIT 7""")
i = 0
for row in ccursor:
  d2011[ i ] = row[0]
  i += 1

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)

ax.bar( d2011, [2,2,2,2,2,2,2], bottom=[10,10,10,10,10,10,10], ec='r',fc='r', label='2011')
ax.bar( np.arange(366), cnts / float(2011-1893+1) * 100.0, fc='b', ec='b' )
sts = mx.DateTime.DateTime(2000,1,1)
ets = mx.DateTime.DateTime(2001,1,1)
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
ax.set_title("Ames Warmest 7 Daily High Temperatures of the Year")
ax.set_ylabel("Frequency [%]")
ax.set_xlabel("[1893-2010] * 2011 data thru 27 June")
ax.set_xlim(90,305)
ax.legend()
ax.grid(True)


fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
