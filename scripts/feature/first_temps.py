import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

mins = []
avgs = []
maxs = []

for low in range(0,32):
    ccursor.execute("""
    SELECT sday, day, station, low from alldata_ia WHERE low <= %s
    and month > 7 ORDER by sday ASC LIMIT 10
    """ , (low,))
    sday = None
    years = []
    stations = []
    for row in ccursor:
        if sday is None:
            sday = row[0]
        if sday != row[0]:
            continue
        if row[1].year not in years:
            years.append( row[1].year )
        stations.append( row[2])
    years.sort()
    print low, sday, years, stations
    
d2010 = []
for high in range(32,81):
    ccursor.execute("""
    SELECT min(m), avg(m), max(m) from
     (SELECT year, min(extract(doy from day)) as m from alldata
    where stationid = 'ia0200' and year = 2010 and
    high >= %s GROUP by year) as foo 
    """ , (high,))
    row = ccursor.fetchone()
    d2010.append( row[0] )
    
import matplotlib.pyplot as plt
import numpy as np
fig = plt.figure()
ax = fig.add_subplot(111)

ax.plot(mins, np.arange(32,81), lw=3, label="Earliest")
ax.plot(avgs, np.arange(32,81), lw=3, label="Average")
ax.plot(maxs, np.arange(32,81), lw=3, label="Latest")
ax.plot(d2010, np.arange(32,81), lw=3, label="2010")
ax.set_xticks( (1,32,60,91,121,152) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun') )
ax.grid(True)
ax.legend(loc=4)
ax.set_ylabel("Temperature ${^\circ}$F")
ax.set_title("First Temperature Exceedance after 1 Jan\n Ames [1893-2010]")
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')