import iemdb
import numpy
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

totals = []
days = []
years = []

for yr in range(1893,2013):
    ccursor.execute("""SELECT day, snow
        from alldata_ia where
        station = 'IA2203' and day > '%s-06-01' 
        and day < '%s-06-01' and snow > 0.01 ORDER by day ASC""" % (yr, yr+1))
    running = None
    last = None
    total = 0
    events = 0
    for row in ccursor:
        snow = row[1]
        total += snow
        day = row[0]
        if last is None:
            events += 1
            last = day
            running = snow
            continue
        if (day - last).days == 1:
            running += snow
            last = day
        else:
            events += 1
            running = None
            last = None
    days.append( events )
    totals.append( total )
    years.append( yr )
 
totals[-1] = 45
totals = numpy.array( totals )
days[-1] = 15
days = numpy.array( days)
adays = numpy.average(days)
atotals = numpy.average(totals)
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

ax.scatter(days, totals)
ax.plot([5,40], [atotals,atotals], color='r')
ax.plot([adays, adays], [0,80], color='r')
ax.text(adays, 3, 'Avg: %.1f' % (adays,), color='r')
ax.text(6, atotals+1, 'Avg: %.1f' % (atotals,), color='r')
for y, d, t in zip(years, days, totals):
    if d >= 31 or t > 57 or d < 12 or y > 2011 or t < 11:
        va = 'bottom'
        m = 1
        if y in [2004,2007,1974,1977,1965,1983]:
            va = 'top'
            m = -1
        ax.text(d, t+m, "%s" % (y,), ha='center', va=va)
ax.set_title("1893-2012 Des Moines Snow Totals v Snow Events\nyear shown is the first half of winter season")
ax.set_xlabel("Snowfall Events (trace events excluded), 2013 thru 19 March")
ax.set_ylabel("Total Season Snowfall [inch]")
ax.grid(True)
ax.set_ylim(0,80)
ax.set_xlim(5,40)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
