import iemdb
import numpy
import numpy.ma
OTHER = iemdb.connect('other', bypass=True)
ocursor = OTHER.cursor()

def getsite(station):
    ocursor.execute("""
    SELECT valid, outgoing_sw, incoming_sw from flux2012 where station = %s
    and extract(hour from valid) = 12 and extract(minute from valid) = 0
    and incoming_sw > 0 and outgoing_sw >= 0 ORDER by valid ASC
    """, (station,))
    valid = []
    soil = []
    val2 = []
    for row in ocursor:
        valid.append( row[0] )
        soil.append( row[1] )
        val2.append( row[2] )
    return valid, soil, val2

v1, s1, s2 = getsite('nstl11')
#v2, s2 = getsite('nstlnsp')
s1 = numpy.array( s1 )
s2 = numpy.array( s2 )

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

(fig, ax) = plt.subplots(2,1, sharex=True)

ax[0].plot(v1, s1, label='Upwelling')
ax[0].plot(v1, s2, label='Downwelling')
ax[0].legend(loc=2, prop={'size': 9})

ax[0].set_title("NLAE Flux Site 2012 Data over Corn Crop (local noon each day)")

albedo = s1 / s2
ax[1].bar(v1, albedo, fc='g', ec='g')
ax[1].set_ylabel("Albedo")
ax[1].grid(True)
ax[0].grid(True)

bbox_props = dict(boxstyle="rarrow,pad=0.3", fc="cyan", ec="b", lw=2)
t = ax[1].text(v1[-30], albedo[-1], "Snow!", ha="right", va="center", rotation=15,
            size=10,
            bbox=bbox_props)
bb = t.get_bbox_patch()
bb.set_boxstyle("rarrow", pad=0.6)

ax[0].xaxis.set_major_locator(
                               mdates.MonthLocator(interval=1)
                               )
ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%-d\n%b'))
ax[0].set_ylabel("Short Wave Rad $W m^{-2}$")

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')