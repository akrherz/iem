
import iemdb
import numpy
import iemplot
coop = iemdb.connect('asos', bypass=True)
c = coop.cursor()
# Yearly totals
"""
c.execute("select substr(d,0,5) as yr, count(*) from (select to_char(valid, 'YYYYMMDDHH24') as d, count(*) from alldata where station = 'DSM' and metar ~* 'TS' and valid > '1973-01-01' GROUP by d) as foo GROUP by yr ORDER by yr ASC")

yrtotals = []
for row in c:
  yrtotals.append( row[1] )

# Now we do hourly total
c.execute("select substr(d,9,2) as hr, count(*) from (select to_char(valid, 'YYYYMMDDHH24') as d, count(*) from alldata where station = 'DSM' and metar ~* 'TS' and valid > '1973-01-01' GROUP by d) as foo GROUP by hr ORDER by hr ASC")

hrtotals = []
for row in c:
  hrtotals.append( row[1] )

# Now we do hourly total
c.execute("select substr(d,9,2) as hr, count(*) from (select to_char(valid, 'YYYYMMDDHH24') as d, count(*) from t2010 where station = 'DSM' and metar ~* 'TS' and valid > '1973-01-01' GROUP by d) as foo GROUP by hr ORDER by hr ASC")

h2010totals = []
for row in c:
  h2010totals.append( row[1] )
"""

yrtotals = [262L, 224L, 182L, 156L, 191L, 155L, 158L, 184L, 170L, 273L, 225L, 198L, 167L, 199L, 151L, 107L, 179L, 205L, 220L, 174L, 268L, 161L, 97L, 114L, 137L, 182L, 132L, 115L, 162L, 152L, 114L, 143L, 136L, 148L, 166L, 181L, 150L, 264L]
hrtotals = numpy.array( [277L, 297L, 306L, 318L, 340L, 330L, 319L, 328L, 309L, 241L, 267L, 245L, 235L, 265L, 233L, 230L, 245L, 224L, 236L, 249L, 263L, 281L, 296L, 268L] , 'f')
h2010totals = numpy.array( [14L, 16L, 16L, 18L, 19L, 17L, 14L, 14L, 12L, 10L, 8L, 7L, 6L, 9L, 8L, 4L, 4L, 8L, 9L, 7L, 9L, 10L, 10L, 15L] , 'f')


import matplotlib.pyplot as plt

# make a little extra space between the subplots
#plt.subplots_adjust(wspace=0.5)


def modcolor(rects, aval):
  for rect in rects:
    if rect.get_height() > aval:
      rect.set_facecolor('r')
    else:
      rect.set_facecolor('b')

ax = plt.subplot(211)
ax.set_title("Des Moines ASOS Thunder Reports [1973-2010]")
rects = ax.bar(numpy.arange(1973,2011) - 0.5, yrtotals, color='r')
#modcolor(rects, 46)
#ax.set_ylim(85,110)
#ax.set_xlim(1972.5,2010.5)
ax.set_xlim(1972.5,2010.5)
#plt.xlabel('time')
ax.set_ylabel("Hours w/ Observation")
ax.grid(True)


ax = plt.subplot(212)
rects = ax.bar(numpy.arange(0,24) - 0.33, hrtotals / numpy.sum(hrtotals) * 100., width=0.33, color='b', label='Climatology')
rects = ax.bar(numpy.arange(0,24), h2010totals / numpy.sum(h2010totals) * 100., width=0.33, color='r', label='2010')
#modcolor(rects, 46)
#ax.set_ylim(65,85)
ax.set_xticks( (0,3,6,9,12,15,18,21) )
ax.set_xticklabels( ('Mid', '3 AM', '6 AM', '9 AM', 'Noon', '3 PM', '6 PM', '9 PM') )
ax.set_xlim(-0.33,23.66)
plt.xlabel('(2010 total through 19 September)')
ax.set_ylabel("Frequency %")
ax.grid(True)
ax.legend(ncol=2)

#plt.subplot(313)
#rects = plt.bar(numpy.arange(1973,2011) - 0.5, y2data, color='r' )
#plt.ylim(0,5)
#modcolor(rects, sum(y2data) / float(len(y2data)))
#plt.xlim(1972.5,2010.5)
#plt.ylabel(r"$\mathrm{Avg}\hspace{0.4}\mathrm{Heat}\hspace{0.4}\mathrm{Index}\hspace{0.4}\Delta^{\circ}\mathrm{F}$")
#plt.grid(True)
plt.savefig("test.ps")
#iemplot.makefeature("test")
