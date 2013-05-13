import iemdb
import numpy
import scipy.stats
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

station = 'IA0200'
ccursor.execute("""SELECT day, extract(doy from day), o.high, c.high
  from alldata_ia o JOIN climate c on (c.station = o.station and
  o.sday = to_char(c.valid, 'mmdd')) WHERE o.station = %s and
  sday < '0417' and year > 1892 ORDER by day ASC""", (station,))

data = numpy.zeros( (2014-1893,108), 'f')
days = []
oyear = 1800
for row in ccursor:
    if row[0].year != oyear:
        running = 0
        oyear = row[0].year
    if oyear == 2013:
        days.append( row[0] )
    if row[2] >= row[3]:
        running += 1
    else:
        running -= 1
    data[oyear-1893,row[1]-1] = running

truth = data[-1,:len(days)]
best = 0
theyear = 0
for yr in range(1893,2013):
    cor = numpy.corrcoef(truth, data[yr-1893,:len(days)])[0,1]
    if cor > best:
        print yr, cor
        best = cor
        theyear = yr

lastval = tuple(data[:,len(days)-1])
print 1893 + lastval.index( max(lastval) )
print 1893 + lastval.index( min(lastval) )

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

(fig, ax) = plt.subplots(1,1)

ax.plot(days, data[-1,:len(days)], lw=2,label='2013')
ax.plot(days, data[-2,:len(days)], lw=2,label='2012 Max')
ax.plot(days, data[theyear-1893,:len(days)], lw=2,label='%s' % (theyear,))
ax.plot(days, data[1979-1893,:len(days)], lw=2,label='1979 Min')
ax.xaxis.set_major_formatter(mdates.DateFormatter("%-d %b"))
ax.grid(True)
ax.legend(loc='best', ncol=2)
ax.set_title("Ames 1 Jan to 16 April Net Days\nwith above average daily high temperature")
ax.set_ylabel("Net Days")


fig.savefig('test.ps')

import iemplot
iemplot.makefeature('test')
