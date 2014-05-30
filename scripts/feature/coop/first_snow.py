import iemdb
import numpy

COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
doy = []
snow = []
days = []
for year in range(1964,2010):
    ccursor.execute("""
    SELECT extract(doy from day), day, snow, snowd from alldata 
    where stationid = 'ia0200' and day BETWEEN 
    %s and %s ORDER by day ASC
    """, ('%s-09-01'  % (year,), 
          '%s-04-01' % (year+1,)))
    found = False
    cnt = 0
    for row in ccursor:
        if row[2] >= 1:
            found = True
            d = row[0]
            if d < 180:
                d += 365
            doy.append( d )
            snow.append( row[2] )
        if row[3] > 0 and found:
            cnt += 1
        if row[3] == 0 and found:
            if cnt > 14:
                days.append( 'g' )
            elif cnt > 7:
                days.append( 'b' )
            else:
                days.append( 'r' )
            break
        
import matplotlib.pyplot as plt

#days = numpy.array(days)
print days

fig = plt.figure()
ax = fig.add_subplot(111)

ax.scatter( doy, snow, c=days, s=100)
ax.set_xticks( (274,305,335,365,365+32,365+60) )
ax.set_xticklabels( ('Oct 1','Nov 1', 'Dec 1', 'Jan 1', 'Feb 1', 'Mar 1'))
ax.grid(True)
ax.set_ylabel('Snowfall [inch]')
ax.set_title('Ames First 1"+ Snowfall Date & Amount [1964-2009]\n(dot color is how long snow remained) ')
ax.set_ylim(0,10)
p1 = plt.Rectangle((0, 0), 1, 1, fc="g")
p2 = plt.Rectangle((0, 0), 1, 1, fc="b")
p3 = plt.Rectangle((0, 0), 1, 1, fc="r")
ax.legend((p1, p2,p3), ('> 14 days','7 - 14', '< 7 days'), ncol=3)


fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')