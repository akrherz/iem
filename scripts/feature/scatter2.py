import numpy
from matplotlib import pyplot as plt
import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()


ccursor.execute("""select foo2.yr, foo.avg, foo2.avg from (select 
extract(year from day + '1 month'::interval) as yr, avg((high+low)/2.0)
 from alldata_ia where station = 'IA2203' and month in (1,2) and 
 sday > '0109' GROUP by yr) as foo2 JOIN (select 
 extract(year from day + '1 month'::interval) as yr, avg((high+low)/2.0) 
 from alldata_ia where station = 'IA2203' and month in (12,1) and
  (sday < '0110' or sday > '1130') GROUP by yr) as foo ON (foo2.yr = foo.yr)
  ORDER by foo2.yr ASC""")
x = []
y = []
for row in ccursor:
    x.append( float(row[1]))
    y.append( float(row[2]))

x = numpy.array( x )
print x[-1]
y = numpy.array( y )

fig = plt.figure()
ax = fig.add_subplot(111)

ax.scatter(x, y)
ax.plot([5,35],[5,35])
ax.plot([5,35],[numpy.average(y), numpy.average(y)], color='r')
ax.text(5,numpy.average(y)+0.1, "%.1f" % (numpy.average(y),), color='r')
ax.plot([numpy.average(x), numpy.average(x)],[5,35], color='g')
ax.text(numpy.average(x)+0.1,33, "%.1f" % (numpy.average(x),), color='g')
ax.plot([30.97,30.97],[5,35], color='k')
ax.text(31,7,"31.0\n2012")
ax.set_xlabel("1 Dec - 8 Jan Average Temperature [F]")
ax.set_ylabel("8 Jan - 28 Feb Average Temperature [F]")
ax.set_title("Iowa Average Winter Temperature [Dec,Jan,Feb] (1893-2011)")
ax.set_xlim(5,40)
ax.set_ylim(5,40)
ax.grid(True)

fig.savefig("test.ps")
import iemplot
iemplot.makefeature("test")
#plt.savefig("test.png")
