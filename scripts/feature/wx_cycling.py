import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

import datetime
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

sts = datetime.datetime(2012,11,26)
ets = datetime.datetime(2013,4,23)
interval = datetime.timedelta(days=7)

lbls = []
psigma = []
tsigma = []
aligns = []
align = ['top', 'bottom']

now = sts
while now < ets:
    sdays = []
    for i in range(0,-14,-1):
        sdays.append( (now + datetime.timedelta(days=i)).strftime("%m%d"))
    ccursor.execute("""
    SELECT avg(p), stddev(p), avg(t), stddev(t),
    max(case when year = %s then p else -999 end),
    max(case when year = %s then t else -999 end) from
    (SELECT year, sum(precip) as p, avg((high+low)/2.) as t from alldata_ia
    WHERE station = 'IA0000' and sday in %s GROUP by year) as foo
    
    """ % (now.year, now.year, str(tuple(sdays)),))
    row = ccursor.fetchone()
    
    psigma.append( (row[4] - row[0]) / row[1] )
    tsigma.append( (row[5] - row[2]) / row[3] )
    lbls.append( now.strftime("%-m/%-d"))
    aligns.append( align[ now.month % 2 ] )
    
    now += interval

now = datetime.datetime(1900,1,15)
record = -1
while now > ets:
    sdays = []
    for i in range(0,-14,-1):
        sdays.append( (now + datetime.timedelta(days=i)).strftime("%m%d"))
    ccursor.execute("""
    SELECT avg(p), stddev(p), avg(t), stddev(t),
    max(case when year = %s then p else -999 end),
    max(case when year = %s then t else -999 end) from
    (SELECT year, sum(precip) as p, avg((high+low)/2.) as t from alldata_ia
    WHERE station = 'IA0000' and sday in %s GROUP by year) as foo
    
    """ % (now.year, now.year, str(tuple(sdays)),))
    row = ccursor.fetchone()
    
    if ((row[4] - row[0]) / row[1] ) > 3.5 and ((row[5] - row[2]) / row[3]) < -1.0:
        print now, (row[4] - row[0]) / row[1]
        record = 3
        ntsigma = []
        npsigma = []
    
    if record >= 0:
        npsigma.append( (row[4] - row[0]) / row[1] )
        ntsigma.append( (row[5] - row[2]) / row[3] )
        
        if record == 0:
            ax.plot(ntsigma, npsigma, color='tan', zorder=1)
        record -= 1
        
    
    now += interval

ax.plot(tsigma, psigma, zorder=2)
for l,t,p,a in zip(lbls, tsigma, psigma,aligns):
    ax.text(t,p, l, va=a, zorder=2)

ax.set_xlim(-2,2)
ax.set_ylabel("Precipitation Departure $\sigma$")
ax.set_xlabel("Temperature Departure $\sigma$")
ax.set_title("26 Nov 2012 - 22 Apr 2013 Iowa\n 14 Day Trailing Departures plotted every 7 days")
ax.grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')