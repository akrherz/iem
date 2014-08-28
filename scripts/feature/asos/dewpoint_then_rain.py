import iemdb
import numpy
import mx.DateTime
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

hits = numpy.zeros( (90, 54), 'f')  #woy, 0 to 89
total = numpy.zeros( (90, 54), 'f')

for yr in range(1934,2013):
    acursor.execute("""SELECT distinct to_char(valid, 'mmddHH24') from
    t%s WHERE station = 'DSM' and p01i >= 0.01
    """ % (yr,))
    obs = {}
    for row in acursor:
        obs[row[0]] = True
    acursor.execute("""SELECT to_char(valid, 'mmddHH24') as d, max(round(dwpf::numeric, 0)) from
    t%s WHERE station = 'DSM' and dwpf >= 0 and valid < '2012-10-23 19:00' GROUP by d
    """ % (yr,))
    for row in acursor:
        ts = mx.DateTime.strptime("%s%s" % (yr, row[0]), '%Y%m%d%H')
        hit = False
        for i in range(1,48):
            lkp = (ts + mx.DateTime.RelativeDateTime(hours=i)).strftime("%m%d%H")
            if obs.has_key(lkp):
                hit = True
                break
        if hit:
            hits[ int(row[1]), int(ts.strftime("%W")) ] += 1.0
        total[ int(row[1]), int(ts.strftime("%W")) ] += 1.0

import numpy.ma

hits2 = numpy.ma.array( hits )
hits2.mask = numpy.where( total < 5, True, False)

total2 = numpy.ma.array( total )
total2.mask = numpy.where( total < 5, True, False)
        
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)



res = ax.imshow( hits2 / total2 * 100.0, aspect='auto', rasterized=True,
                 interpolation='nearest')
ax.set_ylim(0.5,90)
ax.set_xticks( numpy.arange(0,55,7) )
ax.set_xlim(-0.5, 53.5)
ax.set_ylabel("Dew Point Temperature $^{\circ}\mathrm{F}$")
ax.set_xlabel("Week of Year")
ax.set_title("Frequency of Measurable Precip for Des Moines (1934-2012)\nFor 48 Hour Period after Observed Dew Point Temperature")
ax.set_xticklabels( ('Jan 1', 'Feb 19', 'Apr 8', 'May 27', 'Jul 15', 'Sep 2', 'Oct 21', 'Dec 9'))
ax.grid(True)
clr = fig.colorbar(res)
clr.ax.set_ylabel("%")

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')