import iemdb
import mesonet
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""SELECT day, snow from alldata_ia where
 station = 'IA2203' and snow >= 6 ORDER by day DESC LIMIT 11""")

import matplotlib.pyplot as plt
import numpy
import matplotlib.patheffects as PathEffects

(fig, ax) = plt.subplots(1,1)

for row in ccursor:
    snow = row[1]
    day = row[0]
    acursor.execute("""
    SELECT valid, tmpf, dwpf, p01i from alldata WHERE station = 'DSM'
    and valid BETWEEN '%s'::timestamp - '2 days'::interval and
    '%s 23:49'::timestamp + '2 days'::interval ORDER by valid ASC
    """ % (day, day))
    valid = []
    relh = []
    tmpf = []
    dwpf = []
    t0 = None
    for row in acursor:
        tmpf.append( row[1])
        dwpf.append( row[2])
        relh.append( mesonet.relh(row[1], row[2]) )
        valid.append( row[0] )
        if (t0 is None and row[3] >= 0.01 and row[1] <= 34 and
            row[0].day != valid[0].day):
           t0 = row[0]
    print day, t0, snow
    if t0 is None:
        continue
    x = []
    for v in valid:
        diff = (v - t0).days * 86400 + (v - t0).seconds
        x.append(diff)

    ax.plot( x, tmpf)
    for i in range(len(x)):
        if x[i] > -100600:
            txt = ax.text( x[i], tmpf[i], "%s" % (snow,), va='top', ha='center')
            txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                 foreground="yellow")])

            break

ax.set_xticks(numpy.arange(-86400,86401+(12*3600),3600*6))
ax.set_xticklabels(["-24", "-18", "-12", "-6", "start", "6", "12", "18", "24", "30", "36"])
ax.set_xlim(-86400 - (6*3600), 86400 + (18*3600))
ax.grid()
ax.set_title("Des Moines Air Temperature Timeseries during\npast 10 most recent 6+\" Daily Snowfall Events")
ax.set_xlabel("Time from estimated snowfall start [hours]")
ax.set_ylabel("Temperature $^{\circ}\mathrm{F}$")
import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=12)
ax.legend(loc=2, ncol=2, prop=prop)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
