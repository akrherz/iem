import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
import mx.DateTime
import numpy

sigma = []
sigma88 = []
for i in range(1,224):
    end = mx.DateTime.DateTime(2012,8,11)
    start = end - mx.DateTime.RelativeDateTime(days=i)
    print i, start
    ccursor.execute("""
    SELECT year, sum(precip) from alldata_ia where station = 'IA0000' and
    sday BETWEEN '%s' and '%s' GROUP by year
    """ % (start.strftime("%m%d"), end.strftime("%m%d")))
    data = numpy.zeros( (ccursor.rowcount,), 'f')
    for row in ccursor:
        data[row[0]-1893] = row[1]
        
    avg = numpy.average(data)
    stddev = numpy.std(data)
    
    sigma.insert(0, (data[2012-1893] - avg) / stddev )
    sigma88.insert(0, (data[1988-1893] - avg) / stddev )
    

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

ax.plot(numpy.arange(224), sigma)
ax.plot(numpy.arange(224), sigma88)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')