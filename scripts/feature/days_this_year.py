import iemdb
import numpy
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
ccursor2 = COOP.cursor()

ccursor.execute("""SELECT year, sum(case when high > 79 then 1 else 0 end) from alldata_ia WHERE
 station = 'IA0200' and sday < '0612' GROUP by year ORDER by year ASC""")

years = []
days = []
for row in ccursor:
    years.append( row[0] )
    days.append( row[1] )

days[-1] += 1
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

bars = ax.bar(numpy.array(years)-0.5, days, fc='r', ec='r')
bars[-1].set_facecolor('b')
bars[-1].set_edgecolor('b')
ax.set_xlim(1892,2015)
ax.grid(True)
ax.set_ylabel("Days per Year")
ax.set_xlabel("Chart average: %.1f days" % (numpy.average(numpy.array(days)),))
ax.set_title("1893-2014 Ames Days with 80+$^\circ$F High Temperature\nFor period 1 January - 11 June each year")

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
