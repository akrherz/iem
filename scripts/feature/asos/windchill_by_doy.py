import numpy
import iemdb
import math
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

def wchtidx(tmpf, sped):
    if sped < 3:
        return tmpf
    wci = math.pow(sped,0.16);

    return 35.74 + .6215 * tmpf - 35.75 * wci + .4275 * tmpf * wci

def rect(v):
    if v < 180:
        return v + 366
    return v

def get_station(station):
    counts = numpy.zeros( (732,), 'f')
    acursor.execute("""SELECT valid, 
      tmpf, sknt from alldata where station = %s and tmpf < 40 and
      sknt >= 0 and tmpf > -60
      and valid BETWEEN '1973-01-01' and '2013-01-01' ORDER by valid ASC""", (station,))

    last = None
    for row in acursor:
        f = wchtidx(row[1], row[2]*1.15) #mph
        if f <= 0 and last != row[0].strftime("%Y%m%d"):
            counts[ rect(int(row[0].strftime("%j"))-1) ] += 1.0
            last = row[0].strftime("%Y%m%d")
            
    return counts

counts = get_station("MCW")
counts[365] = counts[364]
counts2 = get_station("DSM")
counts2[365] = counts2[364]
counts3 = get_station("FSD")
counts3[365] = counts3[364]
print counts2[360:370]

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

ax.plot(numpy.arange(1,733), counts / 40.0 * 100.0, label='Mason City')
ax.plot(numpy.arange(1,733), counts2 / 40.0 * 100.0, label='Des Moines')
ax.plot(numpy.arange(1,733), counts3 / 40.0 * 100.0, label='Sioux Falls, SD')
ax.set_xticks( (305,335,365,365+32,365+60,365+91,365+121) )
ax.set_xticklabels( ('Nov 1', 'Dec 1', 'Jan 1', 'Feb 1', 'Mar 1', 'Apr 1','May 1'))

ax.set_xlim(290, 470)
ax.set_ylim(0,100)
ax.set_ylabel("Percentage of Years [%]")
ax.grid(True)
ax.set_title("1973-2012 Daily Frequency of 1+ Sub-Zero $^{\circ}\mathrm{F}$ Wind Chill Ob")
ax.legend()

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
