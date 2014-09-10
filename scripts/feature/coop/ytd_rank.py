import numpy
import iemdb
COOP = iemdb.connect("coop", bypass=True)
ccursor = COOP.cursor()

obs = numpy.zeros((2014-1893, 366), 'f')

ccursor.execute("""
 SELECT year, extract(doy from day), precip from alldata_ia
 where station = 'IA8706' and day >= '1893-01-01'
""")
for row in ccursor:
    obs[int(row[0])-1893,int(row[1])-1] = row[2]

ranks = []
diffs = []
for day in range(114):
    sums = numpy.sum(obs[:,:day], 1)
    d2013 = sums[-1]
    diffs.append( d2013 - max(sums[:-1]) )
    lower = numpy.sum( numpy.where(d2013 > sums, 1, 0) )
    ranks.append( len(sums) - lower )


import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(2,1, sharex=True)

ax[0].plot(range(114), ranks, c='b', label='1931')
ax[0].grid(True)
ax[0].set_title("Waterloo 2013 Year-to-Date Precipitation")
ax[0].set_ylabel("2013 Rank for period 1893-2013")
ax[0].set_xlabel("Thru 24 April 2013")

ax[1].plot(range(114), diffs, c='b', label='1931')
ax[1].grid(True)
ax[1].set_ylabel("2013 Difference from Max [in]")
ax[1].set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax[1].set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax[1].set_xlim(0,122)

plt.tight_layout()
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
