import iemdb
import numpy
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
import matplotlib.pyplot as plt

ccursor.execute("""
select year, sum( case when high >= 60 then 1 else 0 end) from alldata 
where stationid = 'ia0200' and month = 11 and year > 1892
GROUP by year ORDER by year ASC
""")
highs = []
for row in ccursor:
    highs.append( row[1] )
highs = numpy.array( highs )
highs[-1] += 1.

ccursor.execute("""
select year, sum( case when high >= 70 then 1 else 0 end) from alldata 
where stationid = 'ia0200' and month = 11 and year > 1892
GROUP by year ORDER by year ASC
""")
lows = []
for row in ccursor:
    lows.append( row[1] )
lows = numpy.array( lows )

def modbars(rects):
    for rect in rects:
        if rect.get_height() >= 45: # fake
            rect.set_facecolor('r')
        else:
            rect.set_facecolor('b')


fig = plt.figure()
ax = fig.add_subplot(211)
bars = ax.bar( numpy.arange(1893,2011) - 0.3 , highs  , edgecolor='b')
modbars( bars )
ax.set_title("Ames November Days Above High Temperature Threshold")
ax.set_xlim(1892.5, 2010.5)
ax.set_ylabel('Above 60 $^{\circ}\mathrm{F}$')
#ax.set_xticks( (0,3,6,9,12,15,18,21,24,27,30,33))
#ax.set_xticklabels( ('JAN\n2008', 'APR', 'JUL', 'OCT', 'JAN\n2009', 'APR', 'JUL', 'OCT', 'JAN\n2010', 'APR', 'JUL', 'OCT' ))
ax.grid(True)
ax = fig.add_subplot(212)
bars = ax.bar( numpy.arange(1893,2011) - 0.3, lows  , edgecolor='b')
modbars( bars )
#ax.set_ylabel('Low Temperature Days')
ax.set_ylabel('Above 70 $^{\circ}\mathrm{F}$')
ax.set_xlabel('2010 Total Thru 7 Nov')
ax.set_xlim(1892.5, 2010.5)
#ax.set_xticks( (0,3,6,9,12,15,18,21,24,27,30,33))
#ax.set_xticklabels( ('JAN\n2008', 'APR', 'JUL', 'OCT', 'JAN\n2009', 'APR', 'JUL', 'OCT', 'JAN\n2010', 'APR', 'JUL', 'OCT' ))
ax.grid(True)
import iemplot
fig.savefig('test.ps')
iemplot.makefeature('test')
