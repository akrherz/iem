import psycopg2
import numpy
import datetime
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
ccursor = COOP.cursor()

MESOSITE = psycopg2.connect(database='mesosite', host='iemdb', user='nobody')
mcursor = MESOSITE.cursor()

elnino = []
elninovalid = []
mcursor.execute("""SELECT anom_34, monthdate from elnino 
    where monthdate >= '2007-01-01' ORDER by monthdate ASC""")
for row in mcursor:
    elnino.append( float(row[0]) )
    elninovalid.append( row[1] )

elnino = numpy.array(elnino)

ccursor.execute("""
 WITH climo as (
 SELECT month, avg((high+low)/2.) from alldata_ia where station = 'IA0200'
 and day < '2014-05-01' GROUP by month),
 
 obs as (
 SELECT year, month, avg((high+low)/2.) from alldata_ia where station = 'IA0200'
 and day < '2014-05-01' and year > 1899 GROUP by year, month)

 SELECT obs.year, obs.month, obs.avg - climo.avg from obs JOIN climo on
 (climo.month = obs.month) 
 ORDER by obs.year ASC, obs.month ASC

""")
diff = []
valid = []
running  = 0
maxrunning = 0
for row in ccursor:
    #print row
    valid.append( datetime.datetime(row[0], row[1], 1) )
    diff.append( row[2] )
    if row[2] < 0:
        running += 1
    else:
        if running > maxrunning:
            print '----->', running, row[0], row[1]
            maxrunning = running
        running = 0

import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_title("Ames Monthly Departure of Average Temperature\nEl Nino 3.4 Index")
#"""
xticks = []
xticklabels = []
for v in valid:
    if v.month not in [1,7]:
        continue
    if v.month == 1:
        fmt = "%b\n%Y"
    else:
        fmt = "%b"
    xticklabels.append( v.strftime(fmt) )
    xticks.append( v )

bars = ax.bar(valid, diff, fc='r', ec='r', width=30)
for bar in bars:
    if bar.get_xy()[1] < 0:
        bar.set_facecolor('b')
        bar.set_edgecolor('b')

ax2 = ax.twinx()

ax2.plot(elninovalid, elnino, zorder=2, color='k', lw=2.0)
ax2.set_ylabel("El Nino 3.4 Index (line)")

ax.set_ylabel("Avg Temperature Departure [F] (bars)")
#ax.set_xlabel("* Thru 28 May 2013")
ax.grid(True)
ax.set_xticks( xticks )
ax.set_xticklabels( xticklabels )
ax.set_xlim(datetime.datetime(2007,1,1), datetime.datetime(2014,5,1))
#ax.set_ylim(-8,8)
"""
import scipy.stats
for i in range(0,12):
    print len(diff[i:-2]), len(elnino[:-(i+1)])
    print i, numpy.corrcoef(diff[i:-2], elnino[:-(i+1)])[0,1]
#ax.scatter(diff[2:], elnino[:-1])
"""
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
