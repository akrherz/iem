import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

data = []
ccursor.execute("""
 SELECT month, avg(sum) from (SELECT year, month, sum(precip) from alldata where stationid = 'ia8755' 
 and year < 2001 and year > 1970 GROUP by month, year) as foo GROUP by month ORDER by month ASC
""")
for row in ccursor:
    data.append( row[1] )

data2 = []
ccursor.execute("""
 SELECT month, avg(sum) from (SELECT year, month, sum(precip) from alldata where stationid = 'ia8755' 
 and year < 2011 and year > 2000 GROUP by month, year) as foo GROUP by month ORDER by month ASC
""")
for row in ccursor:
    data2.append( row[1] )

import numpy
import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111)

ax.bar(numpy.arange(1,13) - 0.4, data, width=0.4, facecolor='r', label='1970-2000')
ax.bar(numpy.arange(1,13), data2, width=0.4, facecolor='b', label='2000-2010')
ax.set_xlim(0.5,12.5)
ax.set_xticks( numpy.arange(1,13) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )

ax.set_ylabel("Monthly Precipitation [inch]")
ax.set_title("Waukon Monthly Precipitation")
ax.legend()
ax.grid(True)
fig.savefig('test.png')
