# Generate imshow plot of daily hail reports

import iemdb

import numpy.ma

obs = numpy.ma.zeros( (8, 54) , 'f')

hrs = numpy.ma.zeros( (24,54) , 'f')



POSTGIS = iemdb.connect('postgis', bypass=True)
pcursor = POSTGIS.cursor()

pcursor.execute("""
    SELECT extract(year from valid) as yr, extract(week from valid) as d, 
    extract(hour from valid) as hr, count(*) from (select distinct valid, city, magnitude from lsrs 
    where state = 'IA' and type = 'H' and valid < '2011-01-01') as foo 
    GROUP by yr, d, hr
""")

for row in pcursor:
    obs[  row[0]-2003, row[1] -1] += row[3]
    hrs[ row[2], row[1]-1] += row[3]

hrs.mask = numpy.where( hrs == 0, True, False)
obs.mask = numpy.where( obs == 0, True, False)
    
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(211)
ax.grid(True)
res = ax.imshow( obs ,aspect='auto', rasterized=True, interpolation='nearest')
fig.colorbar( res )
ax.set_ylim(-0.5,7.5)
ax.set_yticks( (0,2,4,6))
ax.set_yticklabels( ('2003','2005','2007','2009'))
ax.set_xticks( numpy.arange(0,55,7) )
ax.set_xticklabels( ('Jan 1', 'Feb 19', 'Apr 8', 'May 27', 'Jul 15', 'Sep 2', 'Oct 21', 'Dec 9'))
ax.set_ylabel("Year")
ax.set_title("Iowa Hail Reports [2003-2010]")

ax = fig.add_subplot(212)
res = ax.imshow( hrs ,aspect='auto', rasterized=True, interpolation='nearest' )
ax.grid(True)
ax.set_ylim(-0.5,23.5)
ax.set_yticks( (0,4,8,12,16,20))
ax.set_yticklabels( ('Mid','4 AM','8 AM', 'Noon', '4 PM', '8 PM'))
ax.set_xticks( numpy.arange(0,55,7) )
ax.set_xticklabels( ('Jan 1', 'Feb 19', 'Apr 8', 'May 27', 'Jul 15', 'Sep 2', 'Oct 21', 'Dec 9'))
ax.set_ylabel("Local Hour")
ax.set_xlabel("Week of Year")
fig.colorbar( res )
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')