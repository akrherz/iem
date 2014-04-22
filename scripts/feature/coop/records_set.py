
import pg
import mx.DateTime

conn = pg.connect("coop", "iemdb", user="nobody")

rs = conn.query("SELECT day, high, low from alldata where stationid = 'ia0200' and sday != '0229' and year >= 1893 ORDER by day ASC").dictresult()

hrecords = {}
hyears = [0]*(2010-1893+1)
lrecords = {}
lyears = [0]*(2010-1893+1)
expect = [0]*(2010-1893+1)

for row in rs:
  ts = mx.DateTime.strptime(row['day'], '%Y-%m-%d')
  if ts.year == 1893:
    hrecords[ ts.strftime("%m%d") ] = row['high']
    lrecords[ ts.strftime("%m%d") ] = row['low']
    hyears[ts.year - 1893] += 1
    lyears[ts.year - 1893] += 1
    continue
  if row['high'] > hrecords[ ts.strftime("%m%d") ]:
    hrecords[ ts.strftime("%m%d") ] = row['high']
    hyears[ts.year - 1893] += 1
  if row['low'] < lrecords[ ts.strftime("%m%d") ]:
    lrecords[ ts.strftime("%m%d") ] = row['low']
    lyears[ts.year - 1893] += 1

for year in range(1893,2011):
  #print "%s, %s, %.2f" % (year, years[year-1893], 365.0/(year-1892))
  expect[year-1893] = 365.0/float(year-1892)

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import iemplot

fig = plt.figure()
ax = fig.add_subplot(211)
rects = ax.bar( np.arange(1893,2011), hyears, color='b')
for i in range(len(rects)):
    if rects[i].get_height() > expect[i]:
        rects[i].set_facecolor('r')
ax.plot( np.arange(1893,2011), expect, color='black', label="$365/n$")
ax.set_ylim(0,50)
ax.set_xlim(1893,2010)
ax.grid(True)
ax.legend()
ax.set_ylabel("Records set per year")
ax.set_title("Ames Daily Records Set Per Year")
ax.text(1941, 22, "Max High Temperature")

ax = fig.add_subplot(212)
rects = ax.bar( np.arange(1893,2011), lyears, color='r')
for i in range(len(rects)):
    if rects[i].get_height() > expect[i]:
        rects[i].set_facecolor('b')
ax.plot( np.arange(1893,2011), expect, color='black', label="$365/n$")
ax.set_ylim(0,50)
ax.set_xlim(1893,2010)
ax.grid(True)
ax.legend()
ax.set_ylabel("Records set per year")
ax.text(1941, 22, "Min Low Temperature")


fig.savefig("test.ps")
iemplot.makefeature("test")
