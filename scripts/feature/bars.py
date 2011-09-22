from matplotlib import pyplot as plt
import numpy
import iemplot
import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""select year, min(high), sum(case when high < 70 then 1 else 0 end) from alldata_ia where stationid = 'ia0200' and month = 9 and sday < '0922' GROUP by year ORDER by year ASC""")
cnt = []
minh = []
for row in ccursor:
  minh.append( row[1] )
  cnt.append( row[2] )

cnt[-1] += 1

fig = plt.figure()
ax = fig.add_subplot(211)
bars = ax.bar(numpy.arange(1893,2012) - 0.4, minh, color='b', edgecolor='b')
bars[-1].set_edgecolor('r')
bars[-1].set_facecolor('r')
ax.set_ylabel("Minimum High $^{\circ}\mathrm{F}$")
ax.set_title("1-21 September for Ames [1893-2011]")
ax.grid(True)
ax.set_xlim(1892.5,2011.5)
ax.set_ylim(40,80)

ax2 = fig.add_subplot(212)
bars = ax2.bar(numpy.arange(1893,2012) - 0.4, cnt, color='b', edgecolor='b')
bars[-1].set_edgecolor('r')
bars[-1].set_facecolor('r')
ax2.set_ylabel("Days below 70 $^{\circ}\mathrm{F}$")
ax2.grid(True)
ax2.set_xlim(1892.5,2011.5)



plt.savefig('test.ps')
iemplot.makefeature("test")
