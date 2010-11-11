# Count dew point cycles

import iemdb
asos = iemdb.connect('asos', bypass=True)
c = asos.cursor()

UNDER_50 = 0
OVER_70 = 1
POS = [UNDER_50, OVER_70]

data = [0]*61
#for year in range(1950,2011):
#  c.execute("""SELECT dwpf from t"""+ `year` +""" WHERE dwpf >= -30 and station
#    = 'DSM' and valid > '""" +`year`+"""-08-01' ORDER by valid ASC""")
#  mypos = 1
#  cycles = 0
#  for row in c:
#    if row[0] >= 70 and POS[mypos] == UNDER_50:
#      mypos = 1
#      data[year-1950] += 1
#    if row[0] < 50 and POS[mypos] == OVER_70:
#      mypos = 0

data = [1, 0, 1, 0, 1, 0, 1, 1, 3, 3, 1, 2, 2, 2, 3, 2, 1, 0, 1, 0, 1, 1, 2, 1, 1, 3, 2, 2, 3, 1, 1, 0, 2, 0, 2, 2, 4, 0, 1, 1, 2, 3, 3, 2, 3, 1, 0, 5, 2, 0, 0, 1, 3, 1, 3, 2, 0, 2, 0, 0, 1]

from matplotlib import pyplot as plt
import numpy

ax = plt.subplot(111)
ax.set_title("Des Moines Dew Point Cycles\nAfter 1 August (sub 50 to 70+)")
rects = ax.bar(numpy.arange(1950,2011) - 0.5, data, color='b')
#ax.set_ylim(85,110)
#ax.set_xlim(1972.5,2010.5)
ax.set_xlim(1949.5,2010.5)
#plt.xlabel('time')
ax.set_ylabel("Cycles")
ax.grid(True)

plt.savefig("test.ps")
