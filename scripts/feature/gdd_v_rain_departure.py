import iemdb
COOP = iemdb.connect("coop",  bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
--- SELECT sum(precip), sum(gdd50(high,low)) from climate51 where 
--- station = 'ia0200' and valid BETWEEN '2000-05-01' and '2000-08-04'

SELECT avg(one), avg(two) from (SELECT sum(precip) as one, sum(sdd86(high,low)) as two, year from alldata where 
 stationid = 'ia0200' and sday BETWEEN '0501' and '0805' GROUP by year
 ORDER by year ASC) as foo

 """)
row = ccursor.fetchone()
rain = row[0]
gdd50 = row[1]

ccursor.execute("""
 SELECT sum(precip), sum(sdd86(high,low)), year from alldata where 
 stationid = 'ia0200' and sday BETWEEN '0501' and '0805' GROUP by year
 ORDER by year ASC
 """)
departRain = []
departGDD = []
for row in ccursor:
  departRain.append(float( row[0] - rain ))
  departGDD.append(float( row[1] - gdd50 ))

import numpy
departRain = numpy.array(departRain)
departGDD =numpy.array(departGDD)

import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(211)
ax.set_title("1893-2011 Ames Stress Degree Day (base 86)\n1 May - 5 August Depatures")
ax.scatter(departRain[:-1], departGDD[:-1])
ax.scatter(departRain[-1], departGDD[-1], facecolor='r', label='2011')
ax.set_xlabel("Rainfall Depature [inch]")
ax.set_ylabel("SDD Departure")
ax.grid(True)
ax.legend()

ax2 = fig.add_subplot(212)
bars = ax2.bar(numpy.arange(1893,2012) -0.4, departGDD, facecolor='b')
for bar in bars:
  if bar.get_xy()[1] == 0:
    bar.set_facecolor('r')
ax2.set_ylabel("SDD Departure")
ax2.grid(True)

ax2.set_xlim(1892.5,2011.5)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
