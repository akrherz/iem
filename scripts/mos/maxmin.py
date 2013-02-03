import iemdb
import iemplot

MOS = iemdb.connect('mos', bypass=True)
mcursor = MOS.cursor()
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()
mcursor.execute("SET TIME ZONE 'GMT'")
acursor.execute("SET TIME ZONE 'GMT'")

station = 'DSM'
model = 'NAM'

hmaxv = []
hminv = []
hmos = []
hobs = []
# Extract MOS forecasts
mcursor.execute("""SELECT ftime, max(n_x), min(n_x) from t2012
    WHERE station = 'K%s' and ftime >= '2012-07-02 00:00' and model = '%s'
    and extract(hour from ftime) = 0
    and ftime < '2012-07-26'
    GROUP by ftime ORDER by ftime ASC
""" % (station, model))
for row in mcursor:
    acursor.execute("""SELECT max(tmpf) from t2012
    WHERE station = '%s' and tmpf >= -50 and
    valid BETWEEN 
     ('%s 00:00+00'::timestamp - '12 hours'::interval) 
     and '%s 00:00+00'
    """ % (station, row[0].strftime("%Y-%m-%d"), 
           row[0].strftime("%Y-%m-%d")))
    row2 = acursor.fetchone()

    hmaxv.append( row[1] )
    hminv.append( row[2] )
    hmos.append( (row[2] + row[1]) /2.0 )
    if row2[0] is not None:
        hobs.append( row2[0] )
    print row[0], row2, row[1], row[2]


lmaxv = []
lminv = []
lmos = []
lobs = []
# Extract MOS forecasts
mcursor.execute("""SELECT ftime, max(n_x), min(n_x) from t2012
    WHERE station = 'K%s' and ftime >= '2012-07-01 12:00' and model = '%s'
    and extract(hour from ftime) = 12
    and ftime < '2012-07-25'
    GROUP by ftime ORDER by ftime ASC
""" % (station, model))
for row in mcursor:
    sql = """SELECT min(tmpf) from t2012
    WHERE station = '%s' and tmpf >= -50 and
    valid BETWEEN 
     ('%s 12:00+00'::timestamp - '12 hours'::interval) 
     and '%s 12:00+00'
    """ % (station, row[0].strftime("%Y-%m-%d"), 
           row[0].strftime("%Y-%m-%d"))
    #print sql
    acursor.execute(sql)
    row2 = acursor.fetchone()

    lmaxv.append( row[1] )
    lminv.append( row[2] )
    lmos.append( (row[2] + row[1]) /2.0 )
    if row2[0] is not None:
        lobs.append( row2[0] )
    print row2, row[0], row[1], row[2]

import matplotlib.pyplot as plt
import numpy

hminv = numpy.array( hminv )
hmaxv = numpy.array( hmaxv )
lminv = numpy.array( lminv )
lmaxv = numpy.array( lmaxv )

fig = plt.figure()
ax = fig.add_subplot(111)

#ax.set_title("2010 Des Moines Max/Min Temperature\nObservation vs GFS MOS")

#ax.fill_between(numpy.arange(0,len(maxv)), minv, maxv, color='gray')


ax.set_title('Des Moines Daily Temperatures\n%s Forecast MOS Range & Observations' % (model,))

ax.bar( numpy.arange(1,len(hmaxv)+1) -0.4, hmaxv-hminv, facecolor='pink', 
        bottom=hminv, zorder=1, alpha=0.3, label='Daytime High')
ax.scatter(numpy.arange(1,len(hobs)+1), hobs, s=40, c='red', zorder=10,
           label='Obs')

ax.bar( numpy.arange(1,len(lmaxv)+1) -0.4, lmaxv-lminv, facecolor='lightblue', 
        bottom=lminv, zorder=1, alpha=0.3, label='Overnight Low')
print lobs
ax.scatter(numpy.arange(1,len(lobs)+1), lobs, s=40, c='blue', zorder=10,
           label='Obs')
ax.set_xticks( range(1,27,2) )
ax.set_xlim(0.5, 25.5)
#ax.set_xticklabels( range(1,16,2))
ax.set_xlabel("Day of July 2012")

#ax.scatter( hobs, hmos )
#ax.plot( [-10,100], [-10,100])
#ax.set_ylim(-10,100)
#ax.set_xlim(-10,100)
ax.set_ylabel("Temperature $^{\circ}\mathrm{F}$")
#ax.set_ylabel("GFS MOS $^{\circ}\mathrm{F}$")


#ax = fig.add_subplot(212)
#ax.scatter( lobs, lmos )
#ax.plot( [-20,85], [-20,85])
#ax.set_xlim(-20,85)
ax.set_ylim(60,120)
#ax.set_xlabel("Nighttime Low Temperature $^{\circ}\mathrm{F}$")
#ax.set_ylabel("GFS MOS $^{\circ}\mathrm{F}$")

ax.grid(True)
ax.legend(ncol=2,loc=1)
import iemplot
fig.savefig('test.ps')
iemplot.makefeature('test')
