import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

march = []
ccursor.execute("""
 SELECT year, avg((high+low)/2) from alldata where stationid = 'ia0200'
 and month = 3 and year > 1964 GROUP by year ORDER by year ASC
""")
for row in ccursor:
  march.append( float(row[1]) )

import numpy
cnt = numpy.zeros( (2,28), 'f')
tot = numpy.zeros( (2,28), 'f')
ccursor.execute("""
  SELECT extract(day from day), year, snowd from alldata where stationid = 'ia0200'
  and month = 2 and year > 1964 and year < 2011 and sday != '0229'
""")
for row in ccursor:
  if row[2] > 0:
    cnt[0,row[0]-1] += 1
    tot[0,row[0]-1] += march[row[1]-1965]
  else:
    cnt[1,row[0]-1] += 1
    tot[1,row[0]-1] += march[row[1]-1965]

import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111)

ax.bar( numpy.arange(1,29), tot[1,:] / cnt[1,:], width=0.4, facecolor='r', label='No Snowcover')
ax.bar( numpy.arange(1,29)-0.4, tot[0,:] / cnt[0,:], width=0.4, facecolor='b', label='Snowcover')
ax.set_ylim(30,43)
ax.set_xlim(0.5,28.5)
ax.set_xticks((1,4,8,12,16,20,24,28))
ax.grid()
ax.set_title("Ames [1965-2010] February Snow Cover + March Temps")
ax.set_xlabel("Day of February")
ax.set_ylabel("Average March Temperature $^{\circ}\mathrm{F}$")
ax.legend()
import iemplot
fig.savefig('test.ps')
iemplot.makefeature('test')
