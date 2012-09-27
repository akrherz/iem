import numpy
import iemdb
POSTGIS = iemdb.connect('postgis', bypass=True)
pcursor = POSTGIS.cursor()

counts = numpy.zeros( (5,366), 'f')
accum = numpy.zeros( (5,366), 'f')
counts2 = numpy.zeros( (5,366), 'f')
accum2 = numpy.zeros( (5,366), 'f')

for year in range(2008,2013):
  pcursor.execute("""SELECT extract(doy from issue) as doy, 
  count(*), sum(case when wfo in ('DMX','DVN','ARX','FSD','OAX') then 1 else 0 end) from
  sbw_%s WHERE phenomena in ('SV','TO') and status = 'NEW' and significance = 'W' GROUP by doy ORDER by doy ASC""" % (year,))
  for row in pcursor:
    counts[year-2008, int(row[0])-1] = row[1]
    counts2[year-2008, int(row[0])-1] = row[2]

for i in range(366):
  accum[:,i] = numpy.sum(counts[:,0:i+1], 1)
  accum2[:,i] = numpy.sum(counts2[:,0:i+1], 1)

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(2,1, sharex=True)

for i in range(5):
  e = 366
  if i == 4:
    e = 250
  ax[0].plot(numpy.arange(1,e+1), accum[i,:e], linewidth=2, label='%s' % (2008+i,))
  ax[1].plot(numpy.arange(1,e+1), accum2[i,:e], linewidth=2, label='%s' % (2008+i,))

ax[1].set_xlim(1,367)
ax[1].set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax[1].set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax[1].grid(True)
ax[0].grid(True)
import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=10)
ax[0].legend(loc=4, ncol=3, prop=prop)
ax[0].set_title("NWS Severe T'Storm + Tornado Warnings\nUnited States 2008-2012 (thru 6 Sep 2012)")
ax[1].set_title("NWS Offices covering Iowa [DMX,DVN,ARX,FSD,OAX]")
ax[0].set_ylabel("Count")
ax[1].set_ylabel("Count")

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
