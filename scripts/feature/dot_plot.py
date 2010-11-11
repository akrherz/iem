import numpy
from pyIEM import iemdb
i = iemdb.iemdb()
coop = i['coop']

maymin = []
aprgdd = []

rs = coop.query("SELECT year, min(low) from alldata WHERE month = 5 and stationid = 'ia0200' GROUP by year ORDER by year ASC").dictresult()
for i in range(len(rs)):
  maymin.append( rs[i]['min'] )

rs = coop.query("SELECT year, sum(gdd50(high,low)) as sum from alldata WHERE month = 5 and stationid = 'ia0200' GROUP by year ORDER by year ASC").dictresult()
for i in range(len(rs)):
  aprgdd.append( rs[i]['sum'] )

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)
xy = ax.plot(maymin, aprgdd, 'd', markersize=8, markerfacecolor='blue')

fig.savefig("test.png")
