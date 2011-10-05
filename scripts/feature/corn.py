
# VT 1135
# R2 1660
import mx.DateTime
import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

days = []
VTs = []
R2s = []
for yr in range(1951,2012):
  ccursor.execute("""SELECT day, gdd50(high,low) from alldata_ia where
  station = 'IA0200' and month in (5,6,7,8,9,10) and year = %s 
  ORDER by day ASC""", (yr,))
  running = 0
  vt = None
  r2 = None
  for row in ccursor:
    running += row[1]
    if vt is None and running > 1135:
      vt = row[0]
    if r2 is None and running > 1660:
      r2 = row[0]
  days.append((r2 - vt).days)
  if (r2 - vt).days < 20:
    print row
  VTs.append( int(vt.strftime("%j")) )
  R2s.append( int(r2.strftime("%j")) )

import numpy
import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(211)
bars = ax.bar(numpy.arange(1951,2012)-0.4, days)
bars[-1].set_facecolor('r')
bars[-1].set_edgecolor('r')
ax.set_xlim(1950.5,2011.5)
ax.set_title("Ames [1951-2011, plant=1 May] Days between\n Corn VT (1135 GDD) and R2 (1660 GDD) Development Stage")
ax.set_ylabel("Days")
ax.set_ylim(15,30)
ax.grid(True)


ax = fig.add_subplot(212)
ax.plot(numpy.arange(1951,2012), VTs, label="VT (tasseling)")
ax.plot(numpy.arange(1951,2012), R2s, label="R2 (blister)")
ax.set_xlim(1950.5,2011.5)
ax.grid(True)
ax.legend(ncol=2,loc=(0.13,-0.25) )

yticks = []
yticklabels = []
for y in range(175,225):
    ts = mx.DateTime.DateTime(2000,1,1) + mx.DateTime.RelativeDateTime(days=y)
    if ts.day in [1,7,14,21,28]:
        yticks.append( y )
        yticklabels.append( ts.strftime("%-d %b"))
ax.set_yticks( yticks )
ax.set_yticklabels( yticklabels )
ax.set_ylim(174, 225)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
