import iemdb, numpy
COOP =iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ASOS =iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

data = []
ccursor.execute("""
 select year, avg((high+low)/2.) from alldata_ia WHERE 
 station = 'IA2203' and month = 12 and sday < '1221' 
 and year > 1939 GROUP by year ORDER by year ASC
""")
for row in ccursor:
    data.append( float(row[1]) )

wind = []
acursor.execute("""
select extract(year from valid) as yr, avg(sknt) from alldata where station = 'DSM' and extract(month from valid) = 12 and extract(day from valid) < 21 
and valid > '1940-01-01' GROUP by yr ORDER by yr ASC
""")
for row in acursor:
    wind.append( float(row[1]) )
data= numpy.array(data)
avgV = numpy.average(data)
wind = numpy.array(wind)
avgV2 = numpy.average(wind)

import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(211)
bars = ax.bar(numpy.arange(1940,2012)-0.4, data, ec='b', fc='b')
for bar in bars:
    if bar.get_height() > avgV:
        bar.set_facecolor('r')
        bar.set_edgecolor('r')
#ax.plot([1893,2011], [avgV, avgV], color='k')
ax.grid(True)

ax.set_xlim(1939.5,2011.5)
#ax.set_ylim(50,85)
ax.set_title("Des Moines 1-20 December [1940-2011]")
ax.set_ylabel("Average Temp [F]")

ax2 = fig.add_subplot(212)
bars = ax2.bar(numpy.arange(1940,2012)-0.4, wind, ec='b', fc='b')
for bar in bars:
    if bar.get_height() > avgV2:
        bar.set_facecolor('r')
        bar.set_edgecolor('r')
ax2.grid(True)
ax2.set_xlim(1939.5,2011.5)
ax2.set_ylabel("Average Wind Speed [mph]")
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
