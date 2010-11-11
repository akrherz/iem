import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

def doit():
    streak0 = 0
    streak1 = 0
    maxs0 = [0]*366
    maxs1 = [0]*366
    maxp = [0]*366
    ccursor.execute("""SELECT precip, extract(doy from day) as d, day 
    from alldata where stationid = 'ia0200' and year < 2010 ORDER by day ASC""")
    for row in ccursor:
        p = row[0]
        if p < 0.10:
            streak1 += 1
        else:
            streak1 = 0
        if p < 0.001:
            streak0 += 1
        else:
            streak0= 0
        maxs0[int(row[1])-1] = max(streak0, maxs0[int(row[1])-1])
        maxs1[int(row[1])-1] = max(streak1, maxs1[int(row[1])-1])
        maxp[int(row[1])-1] = max(p, maxp[int(row[1])-1])
    return maxs0[:365], maxs1[:365], maxp[:365]

maxs0, maxs1, maxp = doit()

import matplotlib.pyplot as plt
import numpy

fig = plt.figure()
ax = fig.add_subplot(211)
ax.plot(numpy.arange(0,365), maxs1, color='b', label='Below 0.10"')
ax.plot(numpy.arange(0,365), maxs0, color='r', label='No Rain')
ax.set_xticks( (1,31,59,90,120,151,181,212,243,274,303,334) )
ax.set_xticklabels( ("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec") )
ax.set_xlim(0,365)
ax.set_ylim(0,120)
ax.legend(loc=9)
ax.grid(True)
ax.set_ylabel('Max Consecutive Days"')
ax.set_title("Ames Precipitation Climatologies [1893-2009]")

ax = fig.add_subplot(212)
ax.bar(numpy.arange(0,365), maxp, facecolor='b', edgecolor='b')
ax.set_xticks( (1,31,59,90,120,151,181,212,243,274,303,334) )
ax.set_xticklabels( ("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec") )
ax.set_xlim(0,356)
ax.set_ylabel("Maximum Daily Rainfall [inch]")
ax.grid(True)
import iemplot
fig.savefig('test.ps')
iemplot.makefeature('test')   