import psycopg2
import numpy
import math
dbconn = psycopg2.connect(database='asos', host='iemdb', user='nobody')
cursor = dbconn.cursor()

cursor.execute("""
   select valid, dwpf from alldata where station = 'DSM' 
   and dwpf >= -50 ORDER by valid ASC
""")
#"""
valid = []
dwpf = []
for row in cursor:
    valid.append( row[0] )
    dwpf.append( row[1] )

maxes = []
years = []
for level in range(50,81):
    maxduration = 0
    maxyear = 0
    running = False
    for v,d in zip(valid, dwpf):
        if round(d) >= level:
            if not running:
                start = v
            running = True
        else:
            if running: # break
                delta = (v - start).days * 86400.0 + (v - start).seconds
                if delta == maxduration:
                    maxyear += ", %s" % (v.year,)
                if delta > maxduration:
                    maxduration = delta
                    maxyear = "%s" % (v.year,)
            running = False

    maxes.append( maxduration )
    years.append( maxyear )
#"""
#print maxes
#print years
maxes = [7477200.0, 7452000.0, 7437600.0, 6494400.0, 6469200.0, 4813200.0, 3956400.0, 3952800.0, 3556800.0, 3549600.0, 3265200.0, 3261600.0, 2242800.0, 1890000.0, 1501200.0, 1400400.0, 1242000.0, 1206000.0, 1191600.0, 810000.0, 810000.0, 806400.0, 806400.0, 799200.0, 273600.0, 183600.0, 172800.0, 86400.0, 46800.0, 25200.0, 14400.0]
maxes = numpy.array(maxes) / 86400.0
#years = [1998, 1998, 1998, 1998, 1998, 2010, 2010, 2010, 2011, 2011, 2011, 2011, 2011, 1943, 1999, 1999, 1999, 1999, 1999, 2000, 2000, 2000, 2000, 2000, 2011, 2001, 2001, 2000, 2001, 1939, 1933]
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)

ax.bar(numpy.arange(50,81)-0.4, maxes, width=0.8, fc='green', ec='green')
for i, (d, v) in enumerate(zip(numpy.arange(50,81), maxes)):
    ax.text(d, v + 0.2, "%s" % (years[i],), rotation=90, va='bottom', ha='center')

ax.set_ylabel("Days")
ax.set_ylim(0,99)
ax.set_xlim(49.5, 80.5)
ax.set_title("1933-2012 Des Moines Maximum Period\nat or above given Dew Point")
ax.set_xlabel(r"Dew Point $^\circ$F")
ax.grid(True)

fig.savefig('test.svg')
import iemplot
iemplot.makefeature('test')
