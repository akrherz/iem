import iemdb
import math
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

def wchtidx(tmpf, sped):
  if (sped < 3):
    return tmpf
  wci = math.pow(sped,0.16);

  return 35.74 + .6215 * tmpf - 35.75 * wci + \
     + .4275 * tmpf * wci

data = []

for yr in range(1933,2012):
    # Query out obs
    found = {}
    acursor.execute("""
    SELECT tmpf, sknt, to_char(valid, 'MMDDHH24') from alldata where station = 'ALO' and sknt >= 0 and tmpf >= -60
    and valid BETWEEN '%s-09-01' and '%s-01-11' and tmpf < 32
    """ % (yr, yr+1))
    for row in acursor:
        f = wchtidx(row[0], row[1]*1.15) #mph
        if f <= 0:
            if yr == 2011:
                print row
            found[ row[2] ] = 1
            
    data.append( len(found.keys()) )

for i in range(1933,2012):
  print i, data[i-1933]

import matplotlib.pyplot as plt
import numpy

data = numpy.array(data)

fig = plt.figure()
ax = fig.add_subplot(111)

ax.set_title("Hours of sub 0$^{\circ}\mathrm{F}$ Wind Chill per Winter\nDes Moines (1 Oct - 10 Jan) [1933-2011] (Present Day Equation)")

bars = ax.bar( numpy.arange(1933,2012)-0.4, data, label='Des Moines', fc='b', ec='b')
bars[-1].set_facecolor('r')
bars[-1].set_edgecolor('r')
ax.plot([1932,2012], [numpy.average(data), numpy.average(data)], color='k')
#ax.scatter( numpy.arange(1950,2010), data2[:-1],color='b', marker='o', s=50, label='Sioux Falls', facecolor='none')
ax.set_ylabel("Total Hours expressed in days")
ax.set_xlabel("Winter Season")
ax.set_xlim(1932,2012)
ax.set_ylim(0,600)
ax.set_yticks( numpy.arange(0,600,48))
ax.set_yticklabels( numpy.arange(0,600,48)/24)
ax.grid(True)
#ax.legend(loc=2)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
