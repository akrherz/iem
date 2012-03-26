import iemdb
import numpy
import psycopg2.extras
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)

ccursor.execute("""
  select o.day, o.station, o.high, o.high - foo.chigh, (o.high - foo.chigh) / foo.sh as hsd, 
  o.low, o.low - foo.clow, (o.low - foo.clow) / foo.sl as lsd from 
  (select sday, station, avg(high) as chigh, stddev(high) as sh, avg(low) as clow, 
   stddev(low) as sl from alldata_ia where year < 2012 and station = 'IA5952' 
   GROUP by sday, station) as foo, alldata_ia o 
  where o.sday = foo.sday and o.station = 'IA5952' and 
  month = 3 and year = 2012 ORDER by o.day ASC""")

high_sigma = []
low_sigma = []
high_departure = []
low_departure = []

for row in ccursor:
  high_sigma.append( row[4] )
  high_departure.append( row[3] )
  low_sigma.append( row[7] )
  low_departure.append( row[6] )

import matplotlib.pyplot as plt

fig = plt.figure()
ax  = fig.add_subplot(211)

ax.bar( numpy.arange(1,22), high_departure, fc='r', width=0.4, label='High')
ax.bar(numpy.arange(1,22)-0.4, low_departure, fc='b', width=0.4, label='Low')
ax.set_xlim(9.5,21.7)
ax.set_title("New Hampton Daily Temperature Departure\n10-21 March 2012 against 1893-2011 Climatology")
ax.set_ylabel("Temp Departure [$^{\circ}\mathrm{F}$ over ave]")
ax.grid(True)
ax.set_ylim(0,50)
ax.legend(loc=2)

ax2  = fig.add_subplot(212)
ax2.bar( numpy.arange(1,22), high_sigma, fc='r', width=0.4)
ax2.bar(numpy.arange(1,22)-0.4, low_sigma, fc='b', width=0.4)
ax2.set_xlim(9.5,21.7)
ax2.set_ylabel("Temp Departure [$\sigma$]")
ax2.grid(True)
ax2.set_ylim(0,5)
ax2.legend(loc=2)
ax2.set_xlabel("Day of March, unofficial data")

import iemplot
fig.savefig('test.ps')
iemplot.makefeature('test')
