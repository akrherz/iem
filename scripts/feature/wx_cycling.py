import psycopg2
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
ccursor = COOP.cursor()
import numpy as np
import datetime
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

sts = datetime.datetime(2014,5,26)
ets = datetime.datetime(2014,9,9)
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
tsigma = np.array(tsigma, 'f')
psigma = np.array(psigma, 'f')
ax.quiver(tsigma[:-1], psigma[:-1], tsigma[1:]-tsigma[:-1], 
          psigma[1:]-psigma[:-1], scale_units='xy', angles='xy', scale=1,
          zorder=1, color='tan')
for l,t,p,a in zip(lbls, tsigma, psigma,aligns):
    # Manual move label some for readiability
    if l == '7/15':
        t = float(t) + 0.1
        p = float(p) + -0.2
    ax.text(t,p, l, va=a, zorder=2)

ax.set_xlim(-3.5,3.5)
ax.set_ylabel("Precipitation Departure $\sigma$")
ax.set_xlabel("Temperature Departure $\sigma$")
ax.set_title("26 May 2014 - 8 Sep 2014 Iowa\n 14 Day Trailing Departures plotted every 7 days")
ax.grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
