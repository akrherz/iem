import iemdb
import datetime
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
 high, low from ncdc_climate71 where station = 'IA0200'
 and extract(month from valid) in (12,1,2,3,4,5) ORDER by dvalid ASC""")
for row in ccursor:
    ts = row[0]
    ts = ts.replace(year=2013)
    if ts.month in (1,2,3,4,5):
        ts = ts.replace(year=2014)
    #if row[0].month == 3 and row[0].day == 1:
    #    cdates.append( ts - mx.DateTime.RelativeDateTime(days=1) )
    #    chighs.append( chighs[-1] )
    #    clows.append( clows[-1] )

    cdates.append( ts )
    chighs.append( row[1] )
    clows.append( row[2] )

chighs = numpy.array(chighs)
clows = numpy.array(clows)


valid = []
tmpf = []
for yr in [2013,2014]:
    acursor.execute("""
 SELECT valid, tmpf from t%s WHERE station = 'DSM'
 and valid > '2013-12-01' ORDER by valid ASC
""" % (yr))
    for row in acursor:
        valid.append( row[0] )
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

sts = datetime.datetime(2013,12,1)
ets = datetime.datetime(2014,5,15)
now = sts
xticks = []
xticklabels = []
while now < ets:
    if now.day == 1 or now.day % 12 == 0:
        xticks.append( now )
        fmt = "%-d"
        if now.day == 1:
            fmt = "%-d\n%b"
        xticklabels.append( now.strftime(fmt))
    
    now += datetime.timedelta(days=1)

ax = fig.add_subplot(111)
ax.bar(cdates, chighs - clows, bottom=clows, fc='lightblue', ec='lightblue',
       label="Daily Climatology")
ax.plot(valid, tmpf, color='r', label='2014 Hourly Obs')
#ax.plot(valid2, tmpf2, color='k', label='2010-11 Hourly Obs')
ax.set_ylabel("Temperature $^{\circ}\mathrm{F}$")
#ax.set_xlabel("7 September 2011 (EDT)")
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)
ax.set_xlim(sts, ets)
ax.set_ylim(-20,95)
ax.legend(loc=2)
ax.axhline(32, linestyle='-.')
ax.grid(True)
ax.set_title("Ames (KAMW) Air Temperature\n1 Dec 2013 - 14 May 2014")
fig.savefig('test.ps')

import iemplot
iemplot.makefeature('test')
