import numpy
import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

MESOSITE = iemdb.connect('mesosite', bypass=True)
mcursor = MESOSITE.cursor()

elnino = [] # Starts 1950
mcursor.execute("""
 SELECT extract(year from monthdate + '1 month'::interval) as yr, avg(anom_34)
 from elnino where extract(month from monthdate) in (12,1,2) GROUP by yr
 ORDER by yr ASC
""")
for row in mcursor:
    elnino.append( float(row[1]) )

elnino2 = [] # Starts 1950
mcursor.execute("""
 SELECT extract(year from monthdate ) as yr, avg(anom_34)
 from elnino where extract(month from monthdate) in (6,7,8) GROUP by yr
 ORDER by yr ASC
""")
for row in mcursor:
    elnino2.append( float(row[1]) )

t = []
ccursor.execute("""SELECT day, (high+low)/2.0 from alldata_ia
 WHERE station = 'IA2203' and day >= '1900-01-01' ORDER by day ASC""")
xticks = []
dates = []
xticklabels = []
for row in ccursor:
    dates.append( row[0] )
    t.append( float(row[1]) )
    if row[0].year > 2009 and row[0].day == 1 and (row[0].month -1) % 3 == 0:
        xticks.append(len(t)-1)
        fmt = "%b"
        if row[0].month == 1:
            fmt = "%b\n%Y"
        xticklabels.append( row[0].strftime(fmt))

t = numpy.array(t)
ma200 = numpy.zeros( numpy.shape(t), 'f')
ma50 = numpy.zeros( numpy.shape(t), 'f')
for i in range(200,len(t)):
    ma200[i] = numpy.average(t[i-200:i])
for i in range(50,len(t)):
    ma50[i] = numpy.average(t[i-50:i])
 
# Figure out the dates of crosses
death = []
golden = []
above = False # Skip to year 2
for i in range(200,len(t)):
    if above and ma50[i] < ma200[i] and dates[i].month > 6:
        above = False
        death.append( int(dates[i].strftime("%j")))
        #print 'Death', dates[i]
    elif not above and ma50[i] > ma200[i] and dates[i].month < 6:
        above = True
        golden.append(int(dates[i].strftime("%j")))
        #print 'Golden', dates[i]
 
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(3,1, figsize=(10,10))

import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=10)

ax[0].plot(numpy.arange(len(t)), t, color='tan', label="Ob")
ax[0].plot(numpy.arange(len(t)), ma50, color='r', label='50 Day')
ax[0].plot(numpy.arange(len(t)), ma200, color='b', label='200 Day')
ax[0].set_xticks(xticks)
ax[0].set_xticklabels(xticklabels)
ax[0].set_xlim(min(xticks), len(t))
ax[0].grid(True)
ax[0].legend(loc='best', ncol=3, prop=prop)
ax[0].set_title("Des Moines Daily Average Temperature [1900-2012]")
ax[0].set_ylabel("Temperature $^{\circ}\mathrm{F}$")

ax[1].set_title("Date of Yearly 'Death Cross' (50DMA breaches 200DMA), JJA ENSO 3.4")
ax[1].scatter(numpy.arange(1901,2013), death)
for yr in range(1950,2013):
    c = 'r'
    if elnino[yr-1950] < 0:
        c = 'b'
    ax[1].text(yr, death[yr-1901], "%.1f" % (elnino2[yr-1950],), color=c)
ax[1].grid(True)
ticks = []
labels = []
for i in numpy.arange(min(death)-1, max(death)+1,5):
    ticks.append(i)
    labels.append( dates[i].strftime("%b %d"))
ax[1].set_yticks(ticks)
ax[1].set_yticklabels(labels)

print len(elnino)

ax[2].set_title("Date of Yearly 'Golden Cross' (50DMA surpasses 200DMA), DJF ENSO 3.4")
ax[2].scatter(numpy.arange(1901,2013), golden)
for yr in range(1950,2013):
    c = 'r'
    if elnino[yr-1950] < 0:
        c = 'b'
    ax[2].text(yr, golden[yr-1901], "%.1f" % (elnino[yr-1950],), color=c)
ax[2].grid(True)
ticks = []
labels = []
for i in numpy.arange(min(golden)-1, max(golden)+1,5):
    ticks.append(i)
    labels.append( dates[i].strftime("%b %d"))
ax[2].set_yticks(ticks)
ax[2].set_yticklabels(labels)

plt.tight_layout()

fig.savefig('test.png')
#import iemplot
#iemplot.makefeature('test')

