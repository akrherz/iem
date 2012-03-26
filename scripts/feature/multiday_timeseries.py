import iemdb
import mx.DateTime
import numpy
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

cdates = []
chighs = []
clows = []
ccursor.execute("""SELECT 
case when extract(month from valid) = 1 then valid + '1 year'::interval else valid end as dvalid,
 high, low from ncdc_climate71 where station = 'ia2203'
 and extract(month from valid) in (12,1,2,3) ORDER by dvalid ASC""")
for row in ccursor:
    ts = mx.DateTime.strptime(row[0].strftime("%Y%m%d"), "%Y%m%d")
    ts += mx.DateTime.RelativeDateTime(year=2011)
    if row[0].month in (1,2,3):
        ts += mx.DateTime.RelativeDateTime(year=2012)
    if row[0].month == 3 and row[0].day == 1:
        cdates.append( ts - mx.DateTime.RelativeDateTime(days=1) )
        chighs.append( chighs[-1] )
        clows.append( clows[-1] )

    cdates.append( ts )
    chighs.append( row[1] )
    clows.append( row[2] )

chighs = numpy.array(chighs)
clows = numpy.array(clows)


valid = []
tmpf = []
for yr in [2011,2012]:
    acursor.execute("""
 SELECT valid, tmpf from t%s WHERE station = 'DSM'
 and valid > '2011-12-01' ORDER by valid ASC
""" % (yr))
    for row in acursor:
        ts = mx.DateTime.strptime(row[0].strftime("%Y%m%d%H%M"), "%Y%m%d%H%M")
        valid.append( ts )
        tmpf.append( row[1] )

valid2 = []
tmpf2 = []
#for yr in [2010,2011]:
#    acursor.execute("""
# SELECT valid, tmpf from t%s WHERE station = 'DSM'
# and valid > '2010-12-01' and valid < '2011-01-25' ORDER by valid ASC
#""" % (yr))
#    for row in acursor:
#        ts = mx.DateTime.strptime(row[0].strftime("%Y%m%d%H%M"), "%Y%m%d%H%M")
#        valid2.append( ts + mx.DateTime.RelativeDateTime(years=1) )
#        tmpf2.append( row[1] )


import matplotlib.pyplot as plt
import matplotlib.font_manager 
prop = matplotlib.font_manager.FontProperties(size=12) 

fig = plt.figure()

sts = mx.DateTime.DateTime(2012,2,1)
ets = mx.DateTime.DateTime(2012,3,26)
now = sts
xticks = []
xticklabels = []
while now < ets:
    if now.day == 1 or now.day % 7 == 0:
        xticks.append( now )
        fmt = "%-d"
        if now.day == 1:
            fmt = "%-d\n%b"
        xticklabels.append( now.strftime(fmt))
    
    now += mx.DateTime.RelativeDateTime(days=1)

ax = fig.add_subplot(111)
ax.bar(cdates, chighs - clows, bottom=clows, fc='lightblue', ec='lightblue',
       label="Daily Climatology")
ax.plot(valid, tmpf, color='r', label='2012 Hourly Obs')
#ax.plot(valid2, tmpf2, color='k', label='2010-11 Hourly Obs')
ax.set_ylabel("Temperature $^{\circ}\mathrm{F}$")
#ax.set_xlabel("7 September 2011 (EDT)")
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)
ax.set_xlim(float(sts), float(ets))
ax.set_ylim(-10,90)
ax.legend(loc=2)
ax.grid(True)
ax.set_title("Des Moines (KDSM) Air Temperature\n1 Feb 2012 - 25 Mar 2012")
fig.savefig('test.ps')

import iemplot
iemplot.makefeature('test')
