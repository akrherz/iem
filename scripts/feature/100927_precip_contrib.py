import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""select year, sum(case when precip > 0.99 then 1 else 0 end) / sum(case when precip < 1.0 and precip >= 0.01 then 1 else 0 end)::numeric, sum(case when precip > 0.99 then precip else 0 end), sum(case when precip < 1.0 then precip else 0 end), sum(case when precip >= 0.01 and precip < 1. then 1 else 0 end), sum(case when precip > 0.99 then 1 else 0 end),
 sum(case when precip < 0.99 then precip else 0 end) from alldata where stationid = 'ia0200' and month in (5,6,7,8) GROUP by year ORDER by year ASC""")

p1_total = []
pl1_total = []
p1_events = []
pl1_events = []

for row in ccursor:
  p1_total.append( row[2] )
  pl1_events.append( row[4] )
  p1_events.append( row[5] )
  pl1_total.append( row[6] )

import matplotlib.pyplot as plt
import numpy

p1_total = numpy.array( p1_total )
pl1_total = numpy.array( pl1_total )
p1_events = numpy.array( p1_events )
pl1_events = numpy.array( pl1_events )

fig = plt.figure()
ax = fig.add_subplot(211)

ax.bar( numpy.arange(1893,2011), p1_total , color='r', label='1+ inch')
ax.bar( numpy.arange(1893,2011), pl1_total, bottom=p1_total, color='b', label='< 1 inch')
ax.set_xlim(1893,2011)
ax.set_ylabel("Total Precipitation [inch]")
ax.legend(ncol=2,loc=9)
ax.set_title("May-Aug Ames Precipitation Contribution\nfrom daily events over and below 1 inch") 
ax.grid(True)

ax = fig.add_subplot(212)

ax.bar( numpy.arange(1893,2011), p1_events, color='r', label='1+ inch')
ax.bar( numpy.arange(1893,2011), pl1_events, bottom=p1_events, color='b', label='< 1 inch')
ax.set_ylabel("Events")
ax.set_xlim(1893,2011)
ax.legend(ncol=2,loc=9)
ax.grid(True)


fig.savefig("test.png")
