import iemdb
import numpy
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
 SELECT day + '4 months'::interval, 
 extract(doy from day + '4 months'::interval), 
 day, snow, high from alldata_ia where 
 station = 'IA2203' 
 and day > '1899-09-01' and day < '2011-09-01' ORDER by day ASC
""")

tots = numpy.zeros( (112,260), 'f')
is_storm = False
for row in ccursor:
    snow = row[3]
    if snow > 0:
        #if not is_storm:
            # We are in a storm
        doy = row[1]
        year = row[0].year
        storm_tot = tots[ year - 1900,-1]
        tots[ year - 1900, doy: ] = storm_tot + snow

import matplotlib.pyplot as plt
import mx.DateTime

maxtot = (numpy.max( tots, 1 )).tolist()
the_max = max( maxtot )
max_year = maxtot.index( the_max ) + 1900
the_min = min( maxtot )
min_year = maxtot.index( the_min ) + 1900

xticks = [1,32,62,93,124,155, 183, 214, 244]
xticklabels = ['1 Sep','1 Oct', '1 Nov', '1 Dec', '1 Jan','1 Feb', '1 Mar', '1 Apr', '1 May']

fig = plt.figure()
ax3 = fig.add_subplot(111)
ax3.plot( numpy.arange(0,260), numpy.average(tots,0), label="Average" )
ax3.plot( numpy.arange(0,260), tots[max_year-1900,:], label="%s - %s (Max)" % (
  max_year -1, max_year,) )
ax3.plot( numpy.arange(0,260), tots[min_year-1900,:], label="%s - %s (Min)" % (
  min_year -1, min_year,) )
ax3.set_xticks(xticks)
ax3.set_xticklabels(xticklabels)
ax3.set_xlim(31,245)
ax3.set_title("Des Moines Total Snowfall\nEach Winter between 1900-2011")
#ax3.plot([32,135], [avgV,avgV], color='k')
ax3.grid(True)   
#ax3.set_ylim(0,31)  
ax3.set_ylabel("Snowfall Total [inch]")
ax3.legend(loc=2)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
