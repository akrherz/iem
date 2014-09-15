
# VT 1135
# R2 1660
import mx.DateTime
import datetime
import iemdb
import numpy as np
from scipy import stats
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

years = []
yields = []
for line in open('/home/akrherz/Downloads/corn.csv'):
    tokens = line.split(",")
    years.append( float(tokens[0]))
    yields.append( float(tokens[1]))
years = np.array(years)
yields = np.array(yields)

h_slope, intercept, r_value, p_value, std_err = stats.linregress(years, yields)
barcolors = []
for year in years:
    expected = h_slope * year + intercept
    if  yields[year - 1951] > expected:
        barcolors.append('g')
    else:
        barcolors.append('r')
barcolors.append('b')

days = []
VTs = []
R2s = []
for yr in range(1951,2014):
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
  if yr == 2013:
    r2 = datetime.date(2013,8,3)
    print vt, r2, running
  days.append((r2 - vt).days)
  if (r2 - vt).days < 20:
    print row
  VTs.append( int(vt.strftime("%j")) )
  R2s.append( int(r2.strftime("%j")) )

VTs = np.array( VTs )
R2s = np.array( R2s )

import numpy
import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(211)
bars = ax.bar(numpy.arange(1951,2014)-0.4, days)
for i, bar in enumerate(bars):
    bar.set_facecolor(barcolors[i])
    bar.set_edgecolor(barcolors[i])
ax.set_xlim(1950.5,2013.5)
ax.set_title("Ames [1951-2013, plant=1 May] Days between\n Corn VT (1135 GDD) and R2 (1660 GDD) Development Stage")
ax.set_ylabel("Days")
ax.set_ylim(15,35)
ax.grid(True)

p1 = plt.Rectangle((0, 0), 1, 1, fc="r")
p3 = plt.Rectangle((0, 0), 1, 1, fc="g")
ax.legend([p1,p3], ["Below Trendline", "Above Trendline"], ncol=4)


ax = fig.add_subplot(212)
bars = ax.bar(numpy.arange(1951,2014)-0.4, R2s - VTs, bottom=VTs)
for i, bar in enumerate(bars):
    bar.set_facecolor(barcolors[i])
    bar.set_edgecolor(barcolors[i])
ax.set_xlim(1950.5,2013.5)
ax.grid(True)
#ax.legend(ncol=2,loc=(0.13,-0.25) )

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
ax.set_xlabel("bar color is Story County corn yield departure from 1951-2012 trend")

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
