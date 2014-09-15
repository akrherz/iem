import mx.DateTime
import numpy
import iemdb, iemplot
COOP = iemdb.connect("coop", bypass=True)
ccursor = COOP.cursor()

lows = []
jdays = []
ylows = []
for yr in range(1894,2010):
    ccursor.execute("""
    SELECT extract(doy from day), low as m from alldata
    where stationid = 'ia0200' and day between '%s-10-01' and '%s-05-01'
    ORDER by m ASC""" % (yr, yr+1))
    minv = 1000.
    for row in ccursor:
        if row[1] <= minv:
            lows.append( float(row[1]) )
            jday = row[0]
            if jday < 180:
                jday += 365
            jdays.append( float(jday) )
            minv = row[1]
    ylows.append( minv )


import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)
ax.scatter( jdays, lows )
#ax.bar(range(1894,2010), ylows)
ax.set_ylabel("Lowest Winter Temperature $^{\circ}\mathrm{F}$")
#ax.set_xlim(1893,2010)
ax.grid(True)
ax.set_xlim(335,440)
ax.set_xticks( (335,350, 365,365+16, 365+32,365+47, 365+60, 365+75) )
ax.set_xticklabels( ('Dec 1', 'Dec 15', 'Jan 1', 'Jan 15', 'Feb 1', 'Feb 15', 'Mar 1','Mar 15'))
ax.set_xlabel("Date of Lowest Temperature")
ax.set_title("Date of Coldest Winter Low Temperature\nAmes [1893-2010] (ties included)")
fig.savefig('test.ps')

iemplot.makefeature('test')