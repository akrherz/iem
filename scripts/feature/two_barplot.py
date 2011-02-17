
import iemdb
import numpy
import iemplot
coop = iemdb.connect('coop', bypass=True)
ccursor = coop.cursor()
import matplotlib.patches as mpatches

ccursor.execute("""
select year, avg((high+low)/2.) from alldata 
where stationid = 'ia0200' and month = 12 
and sday < '1209' and year < 2010 
GROUP by year ORDER by year ASC
""")
yrtot = []
for row in ccursor:
    yrtot.append( float(row[1]) )
ccursor.execute("""
select year, avg((high+low)/2.) from alldata 
where stationid = 'ia0200' and month = 12 
and sday > '1208' and year < 2010 
GROUP by year ORDER by year ASC
""")
yrtot2 = []
for row in ccursor:
    yrtot2.append( float(row[1]) )
yrtot = numpy.array( yrtot )
yrtot2 = numpy.array( yrtot2 )
alle = numpy.sum( numpy.where( yrtot2 > yrtot, 1, 0))
print yrtot.min()
import matplotlib.pyplot as plt

ax = plt.subplot(111)
fancybox = mpatches.FancyBboxPatch(
        [5,0], 15, 50,
        boxstyle='round', alpha=0.2, facecolor='#7EE5DE', zorder=1)
ax.add_patch( fancybox )
ax.set_title("Ames December Temperatures [1893-2009]")
ax.scatter( yrtot, yrtot2, s=40, zorder=2)
ax.plot([0,50],[0,50], color='r')
ax.plot([numpy.average(yrtot),numpy.average(yrtot)], [0,50], 'b--')
ax.plot([0,50], [numpy.average(yrtot2),numpy.average(yrtot2)], 'b--')
#modcolor(rects, 46)
ax.set_ylim(0,50)
ax.set_xlim(0,50)
ax.set_xlabel('Average Temperature (1-8 Dec) $^{\circ}\mathrm{F}$')
ax.set_ylabel('Average Temperature (9-31 Dec) $^{\circ}\mathrm{F}$')
#ax.set_xlim(1972.5,2010.5)
#ax.set_xlim(1972.5,2010.5)
#plt.xlabel('time')
#ax.set_ylabel("Hours w/ Observation")
ax.grid(True)


plt.text(15,42, '18/23 events\nsecond period\nwarmer\n2010=20$^{\circ}\mathrm{F}$', ha='center')
plt.text(45,2, 'All Events\n%s/%s events\nsecond period\nwarmer' % (alle,
                                    len(yrtot)), ha='center')


plt.savefig("test.ps")
iemplot.makefeature("test")
