import iemdb, network
import numpy

COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

#select extract(year from o.day + '2 months'::interval) as yr, sum(case when o.high > c.high then 1 else 0 end), count(*) from alldata_ia o , climate51 c WHERE c.station = o.station and o.station = 'IA0200' and extract(month from c.valid) = extract(month from o.day) and extract(day from c.valid) = extract(day from o.day) and (o.month in (11,12,1) or (o.month = 2 and extract(day from o.day) < 9)) and o.day > '1893-06-01' GROUP by yr ORDER by yr ASC
ccursor.execute("""
 select year, sum(gdd50(high,low)), avg((high+low)/2.0) from alldata_ia
 WHERE station = 'IA0200' and sday < '0323' GROUP by year ORDER by year ASC
""")

years = []
gdd50 = []
avgT = []

for row in ccursor:
    years.append( row[0] )
    gdd50.append( float(row[1])  )
    avgT.append( float(row[2])  )


years = numpy.array( years )
gdd50 = numpy.array( gdd50 )
avgT = numpy.array( avgT )
import matplotlib.pyplot as plt
import iemplot

fig = plt.figure()
ax = fig.add_subplot(211)

ag = numpy.average(gdd50)
bars = ax.bar( years - 0.4, gdd50, fc='b', ec='b')
for bar in bars:
  if bar.get_height() > ag:
    bar.set_facecolor('r')
    bar.set_edgecolor('r')

ax.set_xlim(1892.5, 2013.5)
ax.set_title("Ames Growing Degree Days (base 50)\n 1 January - 22 March [1893-2012]")
ax.grid(True)

ax.set_ylabel('GDD [F]')

ax2 = fig.add_subplot(212)

ag = numpy.average(avgT)
bars = ax2.bar( years - 0.4, avgT, fc='b', ec='b')
for bar in bars:
  if bar.get_height() > ag:
    bar.set_facecolor('r')
    bar.set_edgecolor('r')
ax2.set_xlim(1892.5, 2013.5)
ax2.grid(True)

ax2.set_ylabel('Average Temp [F]')


fig.savefig('test.ps')
iemplot.makefeature('test')
