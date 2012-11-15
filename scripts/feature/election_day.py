import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
import mx.DateTime
import numpy

[R, D] = range(2)
years = numpy.arange(1900,2012,4)
us_results = [R, R, R, D, D, R, R, R, D, D, D, D, D, R, R, D, D, R, R, D, R, R, R, D, D, R, R, D]
ia_results = [R, R, R, D, R, R, R, R, D, D, R, R, D, R, R, R, D, R, R, R, R, R, D, D, D, D, R, D]

highs = []
precip = []
for year in years:
      nov1 = mx.DateTime.DateTime(year, 11, 1)
      firstmon = nov1 + mx.DateTime.RelativeDateTime(weekday=(mx.DateTime.Monday,1))
      tuesday = firstmon + mx.DateTime.RelativeDateTime(days=1)
      print tuesday
      ccursor.execute("""SELECT high, precip from alldata_ia where station = 'IA0000'
      and day = '%s' """ % (tuesday.strftime("%Y-%m-%d"),) )
      row = ccursor.fetchone()
      highs.append( row[0] )
      precip.append( row[1] )

highs = numpy.array(highs)
precip = numpy.array(precip)

import matplotlib.pyplot as plt
import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=12)

(fig, ax) = plt.subplots(2,1, sharex=True)

bars = ax[0].bar(years-2, highs, width=4)
ax[0].plot([1898,2010], [numpy.average(highs), numpy.average(highs)], color='k')
for i in range(len(bars)):
    if ia_results[i] == R:
        bars[i].set_facecolor('r')
    if us_results[i] == R and ia_results[i] == D:
        bars[i].set_facecolor('purple')
    if us_results[i] == D and ia_results[i] == R:
        bars[i].set_facecolor('yellow')
ax[0].grid(True)
ax[0].set_title("Iowa Presidental Election Day Weather & Result")
ax[0].set_xlim(1897.5,2010.5)
ax[0].set_ylabel("High Temperature $^{\circ}\mathrm{F}$")
ax[0].set_ylim(30,80)

bars = ax[1].bar(years-2, precip, width=4)
ax[1].plot([1898,2010], [numpy.average(precip), numpy.average(precip)], color='k')
for i in range(len(bars)):
    if ia_results[i] == R:
        bars[i].set_facecolor('r')
    if us_results[i] == R and ia_results[i] == D:
        bars[i].set_facecolor('purple')
    if us_results[i] == D and ia_results[i] == R:
        bars[i].set_facecolor('yellow')

ax[1].set_ylabel("Precipitation [inch]")

p1 = plt.Rectangle((0, 0), 1, 1, fc="b")
p2 = plt.Rectangle((0, 0), 1, 1, fc="r")
p3 = plt.Rectangle((0, 0), 1, 1, fc="purple")
p4 = plt.Rectangle((0, 0), 1, 1, fc="yellow")
ax[1].legend((p1, p2,p3,p4), ('Both D.','Both R.', 'IA - D., US - R.',
                              'IA - R., US - D.'), ncol=4, loc=(0,1.02),
             prop=prop)
ax[1].grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
      