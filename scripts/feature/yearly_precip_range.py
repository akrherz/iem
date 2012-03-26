import iemdb, network
import numpy

COOP = iemdb.connect('postgis', bypass=True)
ccursor = COOP.cursor()

data1 = []
data2 = []
for yr in range(2005,2012):
    ccursor.execute("""
     select distinct ugc from warnings
      where ugc ~* '^IA' and phenomena in ('BZ') and issue < '%s-05-01' and issue > '%s-10-01'
      and significance = 'W'
    """ % (yr+1, yr))
    data1.append( ccursor.rowcount  )
    
#    ccursor.execute("""
#     select distinct ugc, eventid, significance, phenomena from warnings
#      where ugc ~* '^IA' and phenomena in ('WW','WS','BZ','BS','EC','HS',
#      'IP','IS','SB','SN','WC','ZR') and issue > '%s-02-16' and issue < '%s-05-01'
#      and significance != 'A'
#    """ % (yr+1, yr+1))
#    data2.append( ccursor.rowcount  )
print data1
#print data2
data1 = numpy.array(data1)
#data2 = numpy.array(data2)

import matplotlib.pyplot as plt
import iemplot

fig = plt.figure()
ax = fig.add_subplot(111)

bars = ax.bar( numpy.arange(2006, 2013) - 0.4, data1, 
        facecolor='orange', ec='orange', zorder=1)
#bars2 = ax.bar( numpy.arange(2006, 2013) - 0.4, data2 / 99.0, 
#        facecolor='r', ec='r', zorder=1, bottom=(data1/99.0), label="After 16 Feb")
i = 0
for bar in bars:
    ax.text(2006+i, bar.get_height()/2.0 +5, "%.0f" % (data1[i],), ha='center')
    i += 1
i = 0
#for bar in bars2[:-1]:
#    ax.text(2006+i, bars[i].get_height() + (bar.get_height()/2.0), "%.1f" % (data2[i]/99.0,), ha='center')
#    ax.text(2006+i, (data2[i]/99.0+ data1[i]/99.0) + 0.2, "%.1f" % ((data1[i]+data2[i])/99.0,), ha='center')
#    i += 1
ax.set_xlim(2005.5, 2013)
ax.set_xticks( numpy.arange(2006,2013) )
ax.set_xticklabels( numpy.arange(2006,2013) )
ax.set_title("Iowa Counties with 1+ Blizzard Warning\n 1 October - 1 May [2006-2012]")
ax.grid(True)
#ax.set_ylim(0,100)
ax.legend(loc=1)
ax.set_ylabel('Counties [99 Total]')
ax.set_xlabel("* Year of January Shown, 2012 valid thru 27 Feb")
fig.savefig('test.ps')
iemplot.makefeature('test')
