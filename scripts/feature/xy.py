
from matplotlib import pyplot as plt
import mx.DateTime
import numpy
from scipy import stats

import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
ccursor2 = COOP.cursor()

havgs = numpy.zeros( (372), numpy.float )
hstddev = numpy.zeros( (372), numpy.float )
lavgs = numpy.zeros( (372), numpy.float )
lstddev = numpy.zeros( (372), numpy.float )

# Load up averages and stddevs
ccursor.execute("""
 SELECT sday, avg(high), stddev(high),
 avg(low), stddev(low) from alldata WHERE
 stationid = 'ia0200' and sday != '0229' GROUP by sday 
 ORDER by sday ASC
""")
i = 0
for row in ccursor:
    havgs[i] = row[1]
    hstddev[i] = row[2]
    lavgs[i] = row[3]
    lstddev[i] = row[4]
    i += 1

havgs[365:372] = havgs[:7]
lavgs[365:372] = lavgs[:7]
lstddev[365:372] = lstddev[:7]
hstddev[365:372] = hstddev[:7]


seasontotals = numpy.zeros( (4,7), numpy.float)
seasoncnts = numpy.zeros( (4,7), numpy.float)
lseasontotals = numpy.zeros( (4,7), numpy.float)
lseasoncnts = numpy.zeros( (4,7), numpy.float)

# Loop though the year and find days outside of two sigma
for i in range(0,365):
    ts = mx.DateTime.DateTime(2001,1,1) + mx.DateTime.RelativeDateTime(days=i)
    season = 0
    if ts.month in [3,4,5]:
        season = 1
    elif ts.month in [6,7,8]:
        season = 2
    elif ts.month in [9,10,11]:
        season = 3
    
    ccursor.execute("""
        SELECT year, high, day from alldata where
        stationid = 'ia0200' and sday = '%s'
        and high >= %s and year > 1899
""" % (ts.strftime("%m%d"), float(havgs[i] + (2* hstddev[i]))))
    for row in ccursor:
        # GO get the next ten days
        ts2 = mx.DateTime.strptime(row[2].strftime("%Y-%m-%d"), '%Y-%m-%d')
        ccursor2.execute("""
        SELECT high from alldata where stationid = 'ia0200' and day >= %s
        and day < %s ORDER by day asc
        """, (ts2.strftime("%Y-%m-%d"), (ts2+mx.DateTime.RelativeDateTime(days=7)).strftime("%Y-%m-%d")) )
        j = 0
        for row2 in ccursor2:
            #sigma = (row2[0] - havgs[i+j]) / hstddev[i+j]
            #seasontotals[season,j] += sigma
            if row2[0] < havgs[i+j]:
                seasontotals[season,j] += 1
            seasoncnts[season,j] += 1
            j += 1

    ccursor.execute("""
        SELECT year, low, day from alldata where
        stationid = 'ia0200' and sday = '%s'
        and low <= %s and year > 1899
""" % (ts.strftime("%m%d"), float(lavgs[i] - (2* lstddev[i]))))
    for row in ccursor:
        # GO get the next ten days
        ts2 = mx.DateTime.strptime(row[2].strftime("%Y-%m-%d"), '%Y-%m-%d')
        ccursor2.execute("""
        SELECT low from alldata where stationid = 'ia0200' and day >= %s
        and day < %s ORDER by day asc
        """, (ts2.strftime("%Y-%m-%d"), (ts2+mx.DateTime.RelativeDateTime(days=7)).strftime("%Y-%m-%d")) )
        j = 0
        for row2 in ccursor2:
            #sigma = (row2[0] - lavgs[i+j]) / lstddev[i+j]
            #lseasontotals[season,j] += sigma
            if row2[0] > lavgs[i+j]:
                lseasontotals[season,j] += 1
            lseasoncnts[season,j] += 1
            j += 1

print seasontotals[0]
print seasoncnts[0]
fig = plt.figure()
ax1 = fig.add_subplot(211)

ax1.bar( numpy.arange(0,7) - 0.4, seasontotals[0] / seasoncnts[0] * 100., width=0.2, facecolor='b', label='Winter' )
ax1.bar( numpy.arange(0,7) - 0.2, seasontotals[1] / seasoncnts[1] * 100., width=0.2, facecolor='g', label='Spring' )
ax1.bar( numpy.arange(0,7) , seasontotals[2] / seasoncnts[2] * 100., width=0.2, facecolor='r', label='Summer' )
ax1.bar( numpy.arange(0,7) + 0.2, seasontotals[3] / seasoncnts[3] * 100., width=0.2, facecolor='y', label='Fall' )

ax1.set_title("What happens after really warm day (high greater than 2$\sigma$ )?\nAmes [1900-2010]")
ax1.set_ylabel("High Temp Below Average [%]")
ax1.set_xlim(-0.5, 6.5)

ax1.set_ylim(0,100)
#ax.set_xticks( numpy.arange(0,7))
#ax.set_xticklabels(('Warm Day', 'Tomorrow', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'))
ax1.legend(ncol=2)
ax1.grid(True)

ax = fig.add_subplot(212)

ax.bar( numpy.arange(0,7) - 0.4, lseasontotals[0] / lseasoncnts[0] * 100., width=0.2, facecolor='b', label='Winter' )
ax.bar( numpy.arange(0,7) - 0.2, lseasontotals[1] / lseasoncnts[1] * 100., width=0.2, facecolor='g', label='Spring' )
ax.bar( numpy.arange(0,7) , lseasontotals[2] / lseasoncnts[2] * 100., width=0.2, facecolor='r', label='Summer' )
ax.bar( numpy.arange(0,7) + 0.2, lseasontotals[3] / lseasoncnts[3] * 100., width=0.2, facecolor='y', label='Fall' )

ax.set_title("What happens after really cold day (low less than 2$\sigma$ )?")
ax.set_ylabel("Low Temp Above Average [%]")
ax.set_ylim(0,100)
ax.set_xlim(-0.5, 6.5)
ax.set_xticks( numpy.arange(0,7))
ax.set_xticklabels(('Today', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'))

ax.grid(True)

plt.setp(ax1.get_xticklabels(), visible=False)


fig.savefig("test.ps")
import iemplot
iemplot.makefeature('test')
