import iemdb
import numpy
import copy
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

departures = []

#compute our current departure
ccursor.execute(""" SELECT a.precip - c.precip from alldata_ia a JOIN climate c on (c.station = a.station and a.sday = to_char(c.valid, 'mmdd'))
 WHERE a.station = 'IA0000' and day > now() - '365 days'::interval
 ORDER by day ASC""")
for row in ccursor:
    departures.append( row[0] )

import mx.DateTime
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

# Okay, now we find scenarios for next 180 days
for year in range(1893,2012):
    sts = mx.DateTime.DateTime(year, 11, 29)
    ets = sts + mx.DateTime.RelativeDateTime(days=179)
    ccursor.execute("""SELECT day, a.precip - c.precip from alldata_ia a JOIN climate c 
    on (c.station = a.station and  a.sday = to_char(c.valid, 'mmdd')) where
    a.station = 'IA0000' and day BETWEEN %s and %s ORDER by day ASC""",
    (sts.strftime("%Y-%m-%d"), ets.strftime("%Y-%m-%d")))

    data = copy.deepcopy(departures)
    d2 = [numpy.sum(departures),]
    for row in ccursor:
        data.append( row[1] )
        d2.append( numpy.sum(data[-365:]))
        
    print year, len(d2), d2[0], d2[-1]
    color = 'tan'
    zorder = 1
    if d2[-1] > -4:
        color = 'b'
        zorder= 2
    ax.plot(numpy.arange(181), d2, color=color, zorder=zorder)

sts = mx.DateTime.DateTime(2012,11,29)
ets = sts + mx.DateTime.RelativeDateTime(days=179)
i = 0
now = sts
xticks = []
xticklabels = []
while now < ets:
    if now.day == 1:
        xticks.append( i)
        xticklabels.append( now.strftime("%b"))
    i += 1
    now += mx.DateTime.RelativeDateTime(days=1)

ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)
ax.set_xlabel("29 Nov 2012 - 30 May 2013, only 6 out of 119 years half deficit")
ax.set_ylabel("Running 365 Day Departure [inch]")
ax.set_title("Iowa Precipitation Departure Scenarios\nNext 180 days of historical 1893-2011 data")
ax.set_xlim(-1,182)

ax.grid(True)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')