import iemdb
import mesonet
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

def get2(station):
    acursor.execute("""
    SELECT date(valid), max(tmpf), max(dwpf) from t2012 where
    station  = '%s' and extract(hour from valid + '10 minutes'::interval) = 16
    and extract(minute from valid) > 50 and valid > '2012-07-01'
    GROUP by date ORDER by date ASC
    """ % (station,))
    tmpf = []
    dwpf = []
    feel = []
    for row in acursor:
        tmpf.append( row[1])
        dwpf.append( row[2])
        feel.append( mesonet.heatidx(row[1], mesonet.relh(row[1], row[2])))
        
    return tmpf, dwpf, feel

def get(station):
    icursor.execute("""SELECT day, max_tmpf, max_dwpf from summary_2012 s
    JOIN stations t on (t.iemid = s.iemid) WHERE t.id = '%s' and 
    day >= '2012-07-01' and day < '2012-07-19' ORDER by day ASC""" % (station,))
    tmpf = []
    dwpf = []
    feel = []
    for row in icursor:
        tmpf.append( row[1])
        dwpf.append( row[2])
        
    return tmpf, dwpf, feel

dsm_tmpf, dsm_dwpf, dsm_feel = get('DSM')
amw_tmpf, amw_dwpf, amw_feel = get('AMW')

import matplotlib.pyplot as plt
import numpy

(fig, ax) = plt.subplots(1,1)

ax.bar( numpy.arange(1,19)-0.3, dsm_tmpf, width=0.3, fc='r', ec='r', label="Des Moines Air")
ax.bar( numpy.arange(1,19), amw_tmpf, width=0.3, fc='b', ec='b', label='Ames Air')
ax.bar( numpy.arange(1,19)-0.27, dsm_dwpf, width=0.25, fc='pink', ec='pink', label='Des Moines Dew Point')
ax.bar( numpy.arange(1,19)+0.03, amw_dwpf, width=0.25, fc='skyblue', ec='skyblue', label='Ames Dew Point')
#ax.scatter( numpy.arange(1,19)-0.25, dsm_feel)
#ax.scatter( numpy.arange(1,19)+0.25, amw_feel)
ax.grid()
ax.set_xlim(0.5, 18.5)
ax.set_ylim(55,115)
ax.set_title("Ames & Des Moines Daily Max Air + Dew Point Temp")
ax.set_xlabel("Day of July 2012")
ax.set_ylabel("Temperature $^{\circ}\mathrm{F}$")
import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=12)
ax.legend(loc=2, ncol=2, prop=prop)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')