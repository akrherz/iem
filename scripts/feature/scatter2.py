import numpy
from matplotlib import pyplot as plt
import iemdb
from scipy import stats
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()
import network
nt = network.Table("IA_ASOS")

sql = """
 SELECT extract(day from valid) as day, extract(hour from valid) as hr, station,
 max(p01i) from t2012 where station in %s and valid > '2012-06-01'
 and p01i > 0 GROUP by day, hr, station
""" % (str(nt.sts.keys()).replace("[","(").replace("]",")"))
print sql
acursor.execute(sql)
hrs = []
precip = []
for row in acursor:
    hrs.append( row[1] )
    precip.append( row[3] )

fig = plt.figure()
ax = fig.add_subplot(111)

ax.scatter(hrs, precip, c='r')
ax.set_xlabel("Hour of the day")
ax.set_ylabel("Precipitation [inch]")
ax.set_title("Texas Gulf Coast Wind Direction and Iowa Precipitation\nJune 1970-2011, 2012 thru 10 June")
ax.grid(True)

fig.savefig("test.ps")
import iemplot
iemplot.makefeature("test")
#plt.savefig("test.png")
