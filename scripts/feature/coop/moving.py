import iemdb
import numpy
import matplotlib.pyplot as plt
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
select year, sum(precip) from alldata where station = 'IA0000'
 and month in (1,2,3) and year < 2014 GROUP by year ORDER by year ASC
""")
mt = []
for row in ccursor:
    mt.append( float(row[1]) )

ccursor.execute("""
select year, sum(precip) from alldata where station = 'IA0000'
 and month in (4,5,6) and year < 2014 GROUP by year ORDER by year ASC
""")
mt1 = []
for row in ccursor:
    mt1.append( float(row[1]) )

ccursor.execute("""
select year, sum(precip) from alldata where station = 'IA0000'
 and month in (7,8,9) and year < 2014 GROUP by year ORDER by year ASC
""")
mt2 = []
for row in ccursor:
    mt2.append( float(row[1]) )

ccursor.execute("""
select year, sum(precip) from alldata where station = 'IA0000'
 and month in (10,11,12) and year < 2014 GROUP by year ORDER by year ASC
""")
mt3 = []
for row in ccursor:
    mt3.append( float(row[1]) )
    
mt = numpy.array( mt )
mt1 = numpy.array( mt1 )
mt2 = numpy.array( mt2 )
mt3 = numpy.array( mt3 )
ma = numpy.zeros( (len(mt)-30))
ma1 = numpy.zeros( (len(mt1)-30))
ma2 = numpy.zeros( (len(mt2)-30))
ma3 = numpy.zeros( (len(mt3)-30))
for i in range(30, len(mt)):
    ma[i-30] = numpy.average( mt[i-30:i])
for i in range(30, len(mt1)):
    ma1[i-30] = numpy.average( mt1[i-30:i])
for i in range(30, len(mt2)):
    ma2[i-30] = numpy.average( mt2[i-30:i])
for i in range(30, len(mt3)):
    ma3[i-30] = numpy.average( mt3[i-30:i])

(fig, ax) = plt.subplots(4,1, sharex=True)

ax[0].set_title("1893-2013 Iowa 3 Month Precipitation by Year")

ax[0].bar( numpy.arange(1893,2014) - 0.4, mt, facecolor='#96A3FF', edgecolor="#96A3FF")
ax[0].plot( numpy.arange(1923,2014), ma, c='r', lw=2, zorder=2, label='30 Year MA')
ax[0].set_ylabel("Jan-Feb-Mar [in]", fontsize=9)
ax[0].grid(True)
ax[0].set_xlim(1892.5,2014.5)
ax[0].set_ylim(0,10)

ax[1].bar( numpy.arange(1893,2014) - 0.4, mt1, facecolor='#96A3FF', edgecolor="#96A3FF")
ax[1].plot( numpy.arange(1923,2014), ma1, c='r', lw=2, zorder=2, label='30 Year MA')
ax[1].set_ylabel("Apr-May-Jun [in]", fontsize=9)
ax[1].grid(True)

ax[2].bar( numpy.arange(1893,2014) - 0.4, mt2, facecolor='#96A3FF', edgecolor="#96A3FF")
ax[2].plot( numpy.arange(1923,2014), ma2, c='r', lw=2, zorder=2, label='30 Year MA')
ax[2].set_ylabel("Jul-Aug-Sep [in]", fontsize=9)
ax[2].grid(True)

ax[3].bar( numpy.arange(1893,2014) - 0.4, mt3, facecolor='#96A3FF', edgecolor="#96A3FF")
ax[3].plot( numpy.arange(1923,2014), ma3, c='r', lw=2, zorder=2, label='30 Year MA')
ax[3].set_ylabel("Oct-Nov-Dec [in]", fontsize=9)
ax[3].grid(True)
ax[3].set_xlabel("Red line is trailing 30 year average")
fig.savefig('test.ps')

import iemplot
iemplot.makefeature('test')
