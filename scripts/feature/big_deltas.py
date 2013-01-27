import iemdb
import numpy
import numpy.ma
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

totals = numpy.ma.zeros( (25,), 'f')
counts = 0

for yr in range(1940,2013):
    data = numpy.ma.zeros((366,24), 'f')
    data.mask = numpy.where(data == 0, True, False)
    acursor.execute("""SELECT extract(doy from valid), valid, tmpf 
        from t%s where station = 'DSM'
        and tmpf is not null ORDER by valid ASC""" % (yr,))

    for row in acursor:
        data[ row[0]-1, row[1].hour] = row[2]
        
    for dy in range(0,364):
        today = numpy.ma.max(data[dy,:])
        tomorrow = numpy.ma.max(data[dy+1,:])
        if numpy.ma.is_masked(today) or numpy.ma.is_masked(tomorrow) or (today - tomorrow) < 30:
            continue
        idx = numpy.ma.where(data[dy,:] == today)
        if len(idx[0]) == 0:
            continue
        idx = idx[0][-1]
        hrs = numpy.ma.concatenate([data[dy,idx:], data[dy+1,:idx+1]])
        departure = hrs - today
        #if departure[-2] > -30:
        #    print yr, dy, today, tomorrow, data[dy,:], data[dy+1,:]
        """
        maxdelta = numpy.max(data[dy,:] - data[dy+1,:])
        if maxdelta < 30 or maxdelta is None:
            continue
        # Hit!
        hrdelta = data[dy,:] - data[dy+1,:]
        idx = numpy.where( hrdelta == maxdelta )
        if len(idx[0]) == 0:
            continue
        idx = idx[0][0]
        startval = data[dy,idx]
        hrs = numpy.ma.concatenate([data[dy,idx:], data[dy+1,:idx+1]]) 
        departure = hrs - startval
        if departure[1] < -30:
            print yr, dy, maxdelta, idx, data[dy,idx], data[dy+1,idx], departure
        """
        if not numpy.ma.is_masked(departure):
            counts += 1
            totals += departure 
            ax.plot( numpy.arange(0,25), departure, color='tan')

print totals
print counts
ax.grid(True)
ax.set_xlim(0,24)
ax.set_xticks(numpy.arange(0,25,4))
ax.set_xlabel("Hours After Highest Temperature, %s events with complete data" % (counts,))
ax.set_ylabel("Temperature Change $^{\circ}\mathrm{F}$")
ax.set_title("24 Hour - Hourly Temperature Change\nwhen Daily High Drops 30+$^{\circ}\mathrm{F}$ Des Moines 1940-2012")
ax.plot( numpy.arange(0,25), totals / counts, color='k', linewidth=2, label="Average")
ax.legend()
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')