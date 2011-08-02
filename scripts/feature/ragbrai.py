import mx.DateTime
import iemdb
import math
import numpy
from pyIEM import mesonet
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

def uv(sped, drct2):
  dirr = drct2 * math.pi / 180.00
  s = math.sin(dirr)
  c = math.cos(dirr)
  u = round(- sped * s, 2)
  v = round(- sped * c, 2)
  return u, v

DATES = [ 
[mx.DateTime.DateTime(1973,8,26), mx.DateTime.DateTime(1973,8,31)],
[mx.DateTime.DateTime(1974,8,4), mx.DateTime.DateTime(1974,8,10)],
[mx.DateTime.DateTime(1975,8,3), mx.DateTime.DateTime(1975,8,9)],
[mx.DateTime.DateTime(1976,8,1), mx.DateTime.DateTime(1976,8,7)],
[mx.DateTime.DateTime(1977,7,31), mx.DateTime.DateTime(1977,8,6)],
[mx.DateTime.DateTime(1978,7,30), mx.DateTime.DateTime(1978,8,5)],
[mx.DateTime.DateTime(1979,7,29), mx.DateTime.DateTime(1979,8,4)],
[mx.DateTime.DateTime(1980,7,27), mx.DateTime.DateTime(1980,8,2)],
[mx.DateTime.DateTime(1981,7,26), mx.DateTime.DateTime(1981,8,1)],
[mx.DateTime.DateTime(1982,7,25), mx.DateTime.DateTime(1982,7,31)],
[mx.DateTime.DateTime(1983,7,24), mx.DateTime.DateTime(1983,7,30)],
[mx.DateTime.DateTime(1984,7,22), mx.DateTime.DateTime(1984,7,28)],
[mx.DateTime.DateTime(1985,7,21), mx.DateTime.DateTime(1985,7,27)],
[mx.DateTime.DateTime(1986,7,20), mx.DateTime.DateTime(1986,7,26)],
[mx.DateTime.DateTime(1987,7,19), mx.DateTime.DateTime(1987,7,25)],
[mx.DateTime.DateTime(1988,7,24), mx.DateTime.DateTime(1988,7,30)],
[mx.DateTime.DateTime(1989,7,22), mx.DateTime.DateTime(1989,7,28)],
[mx.DateTime.DateTime(1990,7,22), mx.DateTime.DateTime(1990,7,28)],
[mx.DateTime.DateTime(1991,7,21), mx.DateTime.DateTime(1991,7,27)],
[mx.DateTime.DateTime(1992,7,19), mx.DateTime.DateTime(1992,7,25)],
[mx.DateTime.DateTime(1993,7,25), mx.DateTime.DateTime(1993,7,31)],
[mx.DateTime.DateTime(1994,7,24), mx.DateTime.DateTime(1994,7,30)],
[mx.DateTime.DateTime(1995,7,23), mx.DateTime.DateTime(1995,7,29)],
[mx.DateTime.DateTime(1996,7,21), mx.DateTime.DateTime(1996,7,27)],
[mx.DateTime.DateTime(1997,7,20), mx.DateTime.DateTime(1997,7,26)],
[mx.DateTime.DateTime(1998,7,19), mx.DateTime.DateTime(1998,7,25)],
[mx.DateTime.DateTime(1999,7,25), mx.DateTime.DateTime(1999,7,31)],
[mx.DateTime.DateTime(2000,7,23), mx.DateTime.DateTime(2000,7,29)],
[mx.DateTime.DateTime(2001,7,22), mx.DateTime.DateTime(2001,7,28)],
[mx.DateTime.DateTime(2002,7,21), mx.DateTime.DateTime(2002,7,27)],
[mx.DateTime.DateTime(2003,7,20), mx.DateTime.DateTime(2003,7,26)],
[mx.DateTime.DateTime(2004,7,25), mx.DateTime.DateTime(2004,7,31)],
[mx.DateTime.DateTime(2005,7,24), mx.DateTime.DateTime(2005,7,30)],
[mx.DateTime.DateTime(2006,7,23), mx.DateTime.DateTime(2006,7,29)],
[mx.DateTime.DateTime(2007,7,22), mx.DateTime.DateTime(2007,7,28)],
[mx.DateTime.DateTime(2008,7,20), mx.DateTime.DateTime(2008,7,26)],
[mx.DateTime.DateTime(2009,7,19), mx.DateTime.DateTime(2009,7,25)],
[mx.DateTime.DateTime(2010,7,25), mx.DateTime.DateTime(2010,7,31)],
[mx.DateTime.DateTime(2011,7,24), mx.DateTime.DateTime(2011,7,30)]
]

hindex = numpy.zeros((2012-1973))
uwnd = numpy.zeros((2012-1973))

#output = open('ragbrai.dat', 'w')
for sdate,edate in DATES:
    acursor.execute("""
    SELECT tmpf, dwpf, sknt, drct, valid from t%s WHERE station = 'DSM' and valid BETWEEN '%s 00:00' and '%s 23:59' and tmpf > 0
    and dwpf > 0 and sknt >= 0 and drct >= 0 ORDER by valid ASC
    """ % (sdate.year, sdate.strftime("%Y-%m-%d"), edate.strftime("%Y-%m-%d") ))
    cnt = 0
    tot = 0
    ttot = 0
    utot = 0
    ucnt = 0
    vtot = 0
    for row in acursor:
        ttot += row[0]
        h = mesonet.heatidx(row[0], mesonet.relh(row[0], row[1]))
        if row[4].hour > 5 and row[4].hour < 22:
            u,v = uv(row[2], row[3])
        #output.write("%s,%s,%s,%.1f,%.2f,%.2f\n" % (row[4].strftime("%Y,%m,%d,%H,%M"), row[0], row[1], h, u, v))
            utot += u
            vtot += v
            ucnt += 1
        tot += h
        cnt += 1
    print "%s %3s %4.1f %4.1f %4.1f %4.1f" % (sdate.year, cnt, ttot / float(cnt), tot / float(cnt), utot / float(ucnt), vtot / float(ucnt))
    uwnd[sdate.year-1973] = utot / float(ucnt) * 1.15
    hindex[sdate.year-1973] = tot / float(cnt)
#output.close()

import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(211)
ax.set_xlim(1972.5,2011.5)
ax.set_title("1973-2011 RAGBRAI Weather")
ax.bar(numpy.arange(1973,2012)-0.4, hindex, color='r')
ax.set_ylim(60,100)
ax.set_ylabel("Average Heat Index $^{\circ}\mathrm{F}$")
ax.grid(True)

ax2 = fig.add_subplot(212)
ax2.set_xlim(1972.5,2011.5)
bars = ax2.bar(numpy.arange(1973,2012)-0.4, uwnd, fc='r')
for bar in bars:
    if bar.get_xy()[1] == 0:
        bar.set_facecolor('g')
ax2.set_ylabel("East/West Daytime\n Average Wind Speed [mph]")
ax2.text(1990,5, "Tail-winds")
ax2.text(1990,-5, "Head-winds")

ax2.grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')