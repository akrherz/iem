import iemdb
import numpy
import datetime
import numpy.ma
OTHER = iemdb.connect('other', bypass=True)
ocursor = OTHER.cursor()

def getsite(station):
    ocursor.execute("""
    SELECT valid, hs, le_wpl from flux2013 where station = %s
    and le_wpl BETWEEN -100 and 1000 ORDER by valid ASC
    """, (station,))
    valid = []
    soil = []
    val2 = []
    for row in ocursor:
        valid.append( row[0] )
        soil.append( row[1] )
        val2.append( row[2] )
    return valid, soil, val2

v1, s1, s2 = getsite('nstl30ft')
#v2, s2 = getsite('nstlnsp')
s1 = numpy.array( s1 )
s2 = numpy.array( s2 )
bowen = s1 / s2

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

(fig, ax) = plt.subplots(1,1)
#print v1
#print s2
#ax.plot(v1, s1, label='Sensible')
ax.plot(v1, s2, label='Latent')
#ax[0].legend(loc=2, prop={'size': 9})
ax.set_title("NLAE Flux Site 'NSLT30FT' 1-7 Jan 2013 Latent Heat Flux")
#ax.legend()
ax2 = ax.twinx()
ax2.plot(v1, bowen, color='r')
ax2.set_ylim(-100,100)

ax.annotate("Evaporation +\nSublimation", xy=(datetime.datetime(2013,1,7,15), 50), xycoords='data',
                xytext=(-150, 0), textcoords='offset points',
                bbox=dict(boxstyle="round", fc="0.8"),
                arrowprops=dict(arrowstyle="->",
                connectionstyle="angle3,angleA=90,angleB=0"))
#albedo = s1 / s2
#ax[1].bar(v1, albedo, fc='g', ec='g')
#ax[1].set_ylabel("Albedo")
#ax[1].grid(True)
ax.grid(True)

#bbox_props = dict(boxstyle="rarrow,pad=0.3", fc="cyan", ec="b", lw=2)
#t = ax[1].text(v1[-30], albedo[-1], "Snow!", ha="right", va="center", rotation=15,
#           size=10,
#           bbox=bbox_props)
#bb = t.get_bbox_patch()
#bb.set_boxstyle("rarrow", pad=0.6)

#ax[0].xaxis.set_major_locator(
#                               mdates.MonthLocator(interval=1)
#                               )
ax.xaxis.set_major_formatter(mdates.DateFormatter('%-d\n%b'))
ax.set_ylabel("Latent Heat Flux $W m^{-2}$")

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')