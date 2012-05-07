import iemdb, sys

COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

avgs = {}
ccursor.execute("""SELECT valid, high from climate where station = 'IA0200'""")
for row in ccursor:
  avgs[row[0].strftime("%m%d")] = row[1]

# Get 2012
ccursor.execute("""
 select sday, high from alldata_ia where station = 'IA0200' 
 and year = 2012 ORDER by day ASC
""")
c2012 = 1
for row in ccursor:
  if row[1] >= avgs[row[0]]:
    c2012 += 1

print c2012

vals = []
for yr in range(1900,2013):
  ccursor.execute("""
   select sday, high, day from alldata_ia where station = 'IA0200' and year = %s ORDER by day ASC
  """ % (yr,))
  cnt = 0
  for row in ccursor:
    if row[1] >= avgs[row[0]]:
      cnt += 1
    if cnt == c2012:
      break
  vals.append( int(row[2].strftime("%j")) )

import matplotlib.pyplot as plt
import numpy

fig = plt.figure()
ax = fig.add_subplot(111)
bars = ax.bar( numpy.arange(1900,2013)-0.4, vals, fc='r', ec='r') 
for bar in bars:
  if bar.get_height() > vals[-1]:
    bar.set_facecolor('b')
    bar.set_edgecolor('b')
ax.plot( [1900,2012], [vals[-1],vals[-1]], color='k') 
ax.set_yticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_yticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlim(1899,2013)
ax.grid(True)
ax.set_title("Ames Date of 84th Day Above Average\n1 Jan - 17 Apr 2012 with 84 out of 108 days above average")

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
