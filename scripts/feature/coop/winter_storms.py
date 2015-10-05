import psycopg2
import numpy
import matplotlib.pyplot as plt
import mx.DateTime
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
ccursor = COOP.cursor()

ccursor.execute("""
 SELECT day + '4 months'::interval, 
 extract(doy from day + '4 months'::interval), 
 day, snow, high from alldata_ia where 
 station = 'IA2203' 
 and day > '1899-09-01' ORDER by day ASC
""")

tots = numpy.zeros( (116,260), 'f')
events = numpy.zeros( (116,260), 'f')
is_storm = False
for row in ccursor:
    snow = row[3]
    if snow > 0:
        doy = row[1]
        year = row[0].year
        storm_tot = tots[ year - 1900,-1]
        tots[ year - 1900, doy: ] = storm_tot + snow
        if not is_storm:
           # We are in a storm
           storm_tot = events[ year - 1900,-1]
           events[ year - 1900, doy: ] = storm_tot + 1
        is_storm = True
    else:
        is_storm = False

xticks = [1,32,62,93,124,155, 183, 214, 244]
xticklabels = ['1 Sep','1 Oct', '1 Nov', '1 Dec', '1 Jan','1 Feb', '1 Mar', '1 Apr', '1 May']

fig = plt.figure()
ax3 = fig.add_subplot(111)
v = numpy.average(tots,0)
ax3.plot( numpy.arange(0,260), v / float(max(v)) * 100., lw=2, label="Accumulation %.1f in" % (max(v),) )
v = numpy.average(events,0)
ax3.plot( numpy.arange(0,260), v / float(max(v)) * 100., lw=2, label="Events %.1f" % (max(v),) )
ax3.set_xticks(xticks)
ax3.set_xticklabels(xticklabels)
ax3.set_xlim(31,245)
ax3.set_title("Des Moines Total Snowfall\nEach Winter between 1900-2013")
#ax3.plot([32,135], [avgV,avgV], color='k')
ax3.grid(True)
ax3.set_yticks([0,10,25,50,75,100])
#ax3.set_ylim(0,31)  
ax3.set_ylabel("Percentage of Average Total")
ax3.legend(loc=2)

fig.savefig('test.png')
