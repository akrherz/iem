import iemdb
import numpy
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

def get(extra):
    ccursor.execute("""
SELECT extract (doy from (day + '4 months'::interval)) as doy, 
     sum(case when snowd > 0 then 1 else 0 end), count(*) from alldata_ia where 
     station = 'IA2203' 
     and day > '1899-09-01' and day < '2011-09-01' and 
     extract (year from day + '4 months'::interval) in
     (select year +1 from alldata_ia where station = 'IA2203' and 
     sday = '1225' and snowd %s 0)
     and month in (9,10,11,12,1,2,3,4) GROUP by doy ORDER by doy ASC
    """ % (extra,))
    freq = []
    for row in ccursor:
        freq.append( float(row[1]) / float(row[2]) * 100.0 )
        
    return freq

overall = get(">=")
white = get(">")
brown = get("=")

import matplotlib.pyplot as plt
import mx.DateTime
from matplotlib.patches import Rectangle

fig = plt.figure()
ax3 = fig.add_subplot(111)
ax3.plot( numpy.arange(1, numpy.shape(overall)[0]+1), white, color='b',
          label='White Christmas')
ax3.plot( numpy.arange(1, numpy.shape(white)[0]+1), overall, color='g',
          label='All Events')
ax3.plot( numpy.arange(1, numpy.shape(brown)[0]+1), brown, color='r',
          label='Brown Christmas')

#ax3.plot([0,30],[0,30], color='#F3F3F3')
#ax3.plot([0,30],[numpy.average(after),numpy.average(after)], color='#F3F3F3')
#ax3.plot([numpy.average(before),numpy.average(before)], [0,70], color='#F3F3F3')
#ax3.plot([5.6,5.6], [0,70], color='g')
#ax3.text(20,60, "Season Total", color='k')
##ax3.text(20,57.5, "Above Average", color='r')
#ax3.text(20,55, "Above Average", color='b')
#ax3.text(5.6, 55, "2011\n5.7\"", color='g')
#ax3.set_xlim(-0.5,31)
#ax3.set_ylim(-0.5,70)
xticks = [1,32,62,93,124,155, 183, 214, 244]
xticklabels = ['1 Sep','1 Oct', '1 Nov', '1 Dec', '1 Jan','1 Feb', '1 Mar', '1 Apr', '1 May']
ax3.set_xticks(xticks)
ax3.set_xticklabels(xticklabels)
ax3.set_xlim(32,245)
plt.Rectangle((0, 0), 1, 1, fc="g")
#ax3.plot([32,135], [avgV,avgV], color='k')
ax3.grid(True)    
ax3.legend() 
rect = Rectangle((98, 0), 49, 100, facecolor="#aaaaaa", zorder=1)
ax3.add_patch(rect)
ax3.set_xlabel("")
ax3.set_ylabel("Snowcover Observation Frequency [%]")
ax3.set_title("Des Moines Winter Snowcover Frequency\nbased on Christmas Day Snowcover [1933-2011]")


fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
