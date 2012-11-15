import iemdb
import mx.DateTime
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

sts = mx.DateTime.DateTime(2000, 1, 1)
ets = mx.DateTime.DateTime(2000, 10, 8)
interval = mx.DateTime.RelativeDateTime(days=1)
ranks = []
ranks2 = []
now = sts
while now < ets:
    ccursor.execute("""
    select rank from (
    select year, sum(precip), rank() over (ORDER by sum(precip) ASC) 
    from alldata_ia where station = 'IA0000' and sday < '1009' 
    and sday >= '%s' GROUP by year ORDER by sum ASC
    ) as foo where year = 2012
    """ % (now.strftime("%m%d"),))
    row = ccursor.fetchone()
    ranks.append( row[0] )

    ccursor.execute("""
    select rank from (
    select year, sum(precip), rank() over (ORDER by sum(precip) ASC) 
    from alldata_ia where station = 'IA0000' and sday <= '%s' 
    and sday >= '0101' GROUP by year ORDER by sum ASC
    ) as foo where year = 2012
    """ % (now.strftime("%m%d"),))
    row = ccursor.fetchone()
    ranks2.append( row[0] )
    
    now += interval

import matplotlib.pyplot as plt
import numpy

(fig, ax) = plt.subplots(2,1, sharex=True)

bars = ax[0].bar( numpy.arange(len(ranks))+1, ranks, fc='b', ec='b')
for bar in bars:
    if bar.get_height() == 1:
        bar.set_edgecolor('r')
        bar.set_facecolor('r')

ax[0].set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax[0].set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )

ax[0].set_title("2012 Iowa Precipitation Rank (1893-2012, 120 years)")
ax[0].set_ylabel("Rank (1 = driest)")
ax[0].set_xlabel("From Date to 8 October")
ax[0].grid(True)
ax[0].set_xlim(1, len(ranks))

bars = ax[1].bar( numpy.arange(len(ranks2))+1, ranks2, fc='b', ec='b')
for bar in bars:
    if bar.get_height() == 1:
        bar.set_edgecolor('r')
        bar.set_facecolor('r')
ax[1].set_xlabel("From 1 January to Date")
ax[1].grid(True)
ax[1].set_ylabel("Rank (1 = driest)")


fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
