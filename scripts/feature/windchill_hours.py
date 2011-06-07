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

for yr in range(1950,2011):
    # Query out obs
    found = {}
    acursor.execute("""
    SELECT tmpf, sknt, to_char(valid, 'MMDDHH24') from alldata where station = 'DSM' and sknt >= 0 and tmpf >= -60
    and valid BETWEEN '%s-09-01' and '%s-05-01' and tmpf < 32
    """ % (yr, yr+1))
    for row in acursor:
        f = wchtidx(row[0], row[1]*1.15) #mph
        if f <= -20:
            found[ row[2] ] = 1
            
    data.append( len(found.keys()) )

data2 = []

for yr in range(1950,2011):
    # Query out obs
    found = {}
    acursor.execute("""
    SELECT tmpf, sknt, to_char(valid, 'MMDDHH24') from alldata where station = 'FSD' and sknt >= 0 and tmpf >= -60
    and valid BETWEEN '%s-09-01' and '%s-05-01' and tmpf < 32
    """ % (yr, yr+1))
    for row in acursor:
        f = wchtidx(row[0], row[1]*1.15) #mph
        if f <= -20:
            found[ row[2] ] = 1
            
    data2.append( len(found.keys()) )

for i in range(61):
    print i+1950,data[i],data2[i]

import matplotlib.pyplot as plt
import numpy

fig = plt.figure()
ax = fig.add_subplot(211)

ax.set_title("Hours of sub -20 F Wind Chill per Year\nDes Moines and Sioux Falls, SD [1950-2010]")

ax.scatter( numpy.arange(1950,2010), data[:-1], color='r', marker='+', s=50, label='Des Moines')
ax.scatter( numpy.arange(1950,2010), data2[:-1],color='b', marker='o', s=50, label='Sioux Falls', facecolor='none')
ax.set_ylabel("Hours")
ax.set_xlabel("Winter Season")
ax.set_xlim(1950,2011)
ax.set_ylim(0,500)
ax.set_yticks( numpy.arange(0,500,48))
ax.grid(True)
ax.legend(loc=2)

ax2 = fig.add_subplot(212)
ax2.scatter( data, data2)
ax2.plot([0,450], [0,450])
ax2.set_xlabel('Des Moines Hours')
ax2.set_ylabel('Sioux Falls Hours')
ax2.set_xlim(0,500)
ax2.set_ylim(0,500)
ax2.set_yticks( numpy.arange(0,500,48))
ax2.set_xticks( numpy.arange(0,500,48))

ax2.grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')