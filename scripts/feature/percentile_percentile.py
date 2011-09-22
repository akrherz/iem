import numpy
import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

data = numpy.zeros( (30,2011-1893), numpy.int8 )

for day in range(1,31):
  ccursor.execute("""
  SELECT high from alldata where stationid = 'ia0200' and sday = '06%02i'
  and year > 1892 and year < 2011 ORDER by high ASC
  """ % (day,))
  k = 0
  for row in ccursor:
    data[day-1,k] = row[0]
    k += 1

dbelow = []
dabove = []
sz = 2011-1893
for year in range(1893,2012):
  ccursor.execute("""
  SELECT extract(day from day), high from alldata where stationid = 'ia0200' 
  and year = %s and month = 6
  """ % (year,))
  b25 = 0
  a75 = 0
  for row in ccursor:
    high= row[1]
    p = 100
    for i in range(sz):
      if high < data[row[0]-1,i]:
        p = i / float(sz) * 100.
        break
    if p <= 25:
      b25 += 1
    if p >= 75:
      a75 += 1
  
  dabove.append(a75)
  dbelow.append(b25)

dbelow[-1] += 1
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)

pts = ax.scatter( dbelow[:-1], dabove[:-1])
pts = ax.scatter( dbelow[-1], dabove[-1], color='r')
ax.plot( (30,0), (0,30) )
ax.plot( (15,0), (0,15) , color='#EEEEEE')
ax.set_xlim(-0.5,30)
ax.set_ylim(-0.5,30)
ax.set_xlabel("Days Below 25th Percentile")
ax.set_ylabel("Days Above 75th Percentile")
ax.set_title("Ames Daily High Temperatures for each June [1893-2011]")
ax.grid(True)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
