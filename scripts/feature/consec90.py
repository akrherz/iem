#!/mesonet/python/bin/python
import mx.DateTime
import sys
from pyIEM import iemdb
import numpy
i = iemdb.iemdb()
coop = i['coop']


rs = coop.query("""SELECT year, day, high, low, precip from alldata 
  WHERe stationid = 'ia2203' and day > '1893-01-01'
  ORDER by day ASC"""  ).dictresult()

running = 0
biggest = numpy.zeros( (2012-1893), 'f')
for i in range(len(rs)):
  yr = int(rs[i]['year'])
  if rs[i]['high'] != 99:
    if running > biggest[yr-1893]:
      biggest[yr-1893] = running
    if running > 1:
      print rs[i], running
    running = 0
  else:
    running += 1
biggest[2011-1893] += 1

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)

bars = ax.bar(numpy.arange(1893,2012) - 0.5, biggest , fc='r', ec='r')
bars[-1].set_facecolor('b')
bars[-1].set_edgecolor('b')
ax.set_xlim(1892.5,2011.5)
ax.set_ylabel("Consecuative Days")
ax.set_title("Ames Consecuative Days with highs over 90$^{\circ}\mathrm{F}$\nMaximum by year [1893-2011]")
ax.set_xlabel("*2011 Total thru 18 July")
ax.grid(True)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')

