import mx.DateTime
import numpy
from scipy import stats
import iemdb, iemplot
COOP = iemdb.connect("coop", bypass=True)
ccursor = COOP.cursor()

first = []
last = []
years = []
ccursor.execute("""
 select one.year, two.min, one.max  from (select year, max(extract(doy from day)) from 
 alldata_ia where station = 'IA2203' and month < 7 and snow > 0 GROUP by year) 
 as one , (select year, min(extract(doy from day)) from alldata_ia where station = 'IA2203' 
 and month > 7 and snow > 0 
 and year > 1899 GROUP by year) as two WHERE one.year = two.year 
 ORDER by year 
 """)
for row in ccursor:
    years.append( int(row[0]) )
    first.append( row[2] )
    last.append( row[1] )

first.append(65)
years.append(2012)
last.append(319)
last = numpy.array(last)
first = numpy.array(first)
print len(first), len(last)

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)
bars = ax.barh(years, last - first, left=(first), 
               facecolor='b', edgecolor='b')
d2012 = last[-1] - first[-1]
delta = last - first
#i = 0
for (bar, d) in zip(bars, delta):
    if d >= d2012:
        bar.set_facecolor( 'r' )
        bar.set_edgecolor( 'r' )
#    i += 1
#ax.plot([intercept,intercept+(110.0*h_slope)],[1900,2010], c='#000000')
#ax.set_xticklabels( labels )
#ax.set_xticks( xticks )
ax.set_ylim(1899.5,2015.0)
ax.plot([numpy.average(first), numpy.average(first)],[1900,2012], color='k') 
ax.plot([numpy.average(last), numpy.average(last)], [1900,2012], color='k')

#p1 = plt.Rectangle((0, 0), 1, 1, fc="r")
#p2 = plt.Rectangle((0, 0), 1, 1, fc="y")
#p3 = plt.Rectangle((0, 0), 1, 1, fc="g")
#p4 = plt.Rectangle((0, 0), 1, 1, fc="b")
#ax.legend([p1,p2,p3,p4], ["Warmest 25%","","","Coldest 25%"], ncol=4)
#leg = plt.gca().get_legend()
#ltext  = leg.get_texts()
#plt.setp(ltext, fontsize='small')
ax.set_title("Des Moines [1900-2012] Period between\nLast Snowfall of Winter & First Snowfall of next Winter")
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlabel("*2012 still in progress")


ax.grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')