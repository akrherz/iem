"""
This is a comment
"""
import mx.DateTime
import numpy
from scipy import stats
import iemdb
COOP = iemdb.connect("coop", bypass=True)
ccursor = COOP.cursor()

first = []
last = []
years = []
ccursor.execute("""
 select one.year, two.mj, two.mday, one.max, one.mday  from (select year, max(extract(doy from day)),
 max(day) as mday from 
 alldata_ia where station = 'IA8706' and month < 7 and snow > 0 GROUP by year) 
 as one , (select year, min(extract(doy from day)) as mj, min(day) as mday from 
 alldata_ia where station = 'IA8706' 
 and month > 7 and snow > 0 
 and year > 1885 GROUP by year) as two WHERE one.year = two.year 
 ORDER by year 
 """)
for row in ccursor:
    print "%s,%s,%s,%s,%s" % row
    years.append( int(row[0]) )
    first.append( row[3] )
    last.append( row[1] )

first.append(123)
years.append(2013)
last.append(295)
last = numpy.array(last)
first = numpy.array(first)
print len(first), len(last)

import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects

fig = plt.figure()
ax = fig.add_subplot(111)

bars = ax.barh([1950,1951,1952,1953], [366,366,366,366], fc='#EEEEEE', ec='#EEEEEE')
bars = ax.barh(years, last - first, left=(first), 
               facecolor='b', edgecolor='b')
d2012 = last[-1] - first[-1]
delta = last - first
#i = 0
for (bar, d) in zip(bars, delta):
    if d > d2012:
        bar.set_facecolor( 'r' )
        bar.set_edgecolor( 'r' )
    else:
        txt = ax.text(180, bar.get_y(), "%s - %i days" % (bar.get_y(), d),
                      va='center', color='white')
        txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                 foreground="k")])

#    i += 1
#ax.plot([intercept,intercept+(110.0*h_slope)],[1900,2010], c='#000000')
#ax.set_xticklabels( labels )
#ax.set_xticks( xticks )
ax.set_ylim(1895.5,2014.0)
ax.axvline(numpy.average(first),  color='k') 
ax.axvline(numpy.average(last),  color='k')

#p1 = plt.Rectangle((0, 0), 1, 1, fc="r")
#p2 = plt.Rectangle((0, 0), 1, 1, fc="y")
#p3 = plt.Rectangle((0, 0), 1, 1, fc="g")
#p4 = plt.Rectangle((0, 0), 1, 1, fc="b")
#ax.legend([p1,p2,p3,p4], ["Warmest 25%","","","Coldest 25%"], ncol=4)
#leg = plt.gca().get_legend()
#ltext  = leg.get_texts()
#plt.setp(ltext, fontsize='small')
ax.set_xlim(0,366)
ax.set_title("Waterloo [1893-2013] Snowless Period \nLast Measurable Snowfall of Winter & First Snowfall of next Winter")
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
#ax.set_xlabel("*2012 still in progress")


ax.grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')