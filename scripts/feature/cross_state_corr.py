import iemdb
import numpy 
import mx.DateTime
import scipy.stats
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

def get_data(stid1, stid2):
    corrs = []
    sts = mx.DateTime.DateTime(2001,1,1)
    ets = mx.DateTime.DateTime(2002,1,1)
    now = sts
    while now < ets:
        ccursor.execute("""
    SELECT one.year, one.high, two.high from 
    (SELECT year, high from alldata_ia where station = %s 
     and sday = %s and year < 2012) as one JOIN
    (SELECT year, high from alldata_ia where station = %s 
     and sday = %s and year < 2012) as two ON (one.year = two.year)
        """, (stid1, now.strftime("%m%d"), stid2, now.strftime("%m%d")))
        one = []
        two = []
        for row in ccursor:
            one.append( row[1] )
            two.append( row[2] )
        corrs.append( numpy.corrcoef(one, two)[0,1] )
        now += mx.DateTime.RelativeDateTime(days=1)
    return numpy.array(corrs)

import matplotlib.pyplot as plt
import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=12)

fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_title("Daily High Temperature Correlations (1893-2011)")
#ax.set_ylim(0.4,0.9)
ax.set_ylabel("Correlation Coefficient")
ax.set_xlabel("** Three day smooth applied")
data = get_data('IA0200', 'IA2203')
pltdata = (data[:-2] + data[1:-1] + data[2:]) / 3.0
ax.plot( numpy.arange(1,364), pltdata, label='Ames v. Des Moines')
data = get_data('IA2110', 'IA3290')
pltdata = (data[:-2] + data[1:-1] + data[2:]) / 3.0
ax.plot( numpy.arange(1,364), pltdata, label='Decorah v. Glenwood')
data = get_data('IA4381', 'IA7147')
pltdata = (data[:-2] + data[1:-1] + data[2:]) / 3.0
ax.plot( numpy.arange(1,364), pltdata, label='Keokuk v. Rock Rapids')
data = get_data('IA2110', 'IA7147')
pltdata = (data[:-2] + data[1:-1] + data[2:]) / 3.0
ax.plot( numpy.arange(1,364), pltdata, label='Decorah v. Rock Rapids')

ax.set_xlim(0,366)
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.grid()
ax.legend(loc=3, ncol=2, prop=prop)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
