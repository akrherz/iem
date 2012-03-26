import iemdb
import numpy
import copy
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

climate = {}
ccursor.execute("""SELECT avg(high), stddev(high), sday,
  avg(low), stddev(low) from alldata_ia
  where station = 'IA0200' GROUP by sday""")
for row in ccursor:
  climate[row[2]] = {'stddev': row[1], 'avg': row[0],
       'lstddev': row[4], 'lavg': row[3]}

ccursor.execute("""SELECT day, sday, high, low from alldata_ia 
  where station = 'IA0200'  ORDER by day ASC""")

runningUp = numpy.zeros( (45,), 'f')
maxUp = numpy.zeros( (45,), 'f')
runningDown = numpy.zeros( (45,), 'f')
maxDown = numpy.zeros( (45,), 'f')
lrunningUp = numpy.zeros( (45,), 'f')
lmaxUp = numpy.zeros( (45,), 'f')
lrunningDown = numpy.zeros( (45,), 'f')
lmaxDown = numpy.zeros( (45,), 'f')
for row in ccursor:
  if row[0].year == 2012 and row[0].month == 1 and row[0].day == 1:
    maxUp2012 = copy.deepcopy(maxUp)
    maxDown2012 = copy.deepcopy(maxDown)
    lmaxUp2012 = copy.deepcopy(lmaxUp)
    lmaxDown2012 = copy.deepcopy(lmaxDown)
  #sigma = float((row[2] - climate[row[1]]['avg'])  / climate[row[1]]['stddev'])
  sigma = float(row[2] - climate[row[1]]['avg'])
  sigma10 = int(sigma)
  if sigma10 > 0:
    runningUp[:sigma10] += 1.0
    maxUp = numpy.where(runningUp > maxUp, runningUp, maxUp)
    runningDown[:] = 0
  if sigma10 < 0:
    runningDown[sigma10:] += 1.0
    maxDown = numpy.where(runningDown > maxDown, runningDown, maxDown)
    runningUp[:] = 0

  #sigma = float((row[3] - climate[row[1]]['lavg'])  / climate[row[1]]['lstddev'])
  sigma = float(row[3] - climate[row[1]]['lavg'])  
  sigma10 = int(sigma )
  if sigma10 > 0:
    lrunningUp[:sigma10] += 1.0
    lmaxUp = numpy.where(lrunningUp > lmaxUp, lrunningUp, lmaxUp)
    lrunningDown[:] = 0
  if sigma10 < 0:
    lrunningDown[sigma10:] += 1.0
    lmaxDown = numpy.where(lrunningDown > lmaxDown, lrunningDown, lmaxDown)
    lrunningUp[:] = 0



import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)

ax.plot(numpy.arange(1,46) / 1.0, maxUp, color='r', label="High Above")
ax.plot(numpy.arange(1,46) / 1.0, lmaxUp, color='pink', label="Low Above")
ax.plot(numpy.arange(-45,0) / 1.0,maxDown, color='b',label="High Below")
ax.plot(numpy.arange(-45,0) / 1.0, lmaxDown, color='skyblue', label="Low Below")

ax.plot(numpy.arange(1,46) / 1.0, maxUp2012, color='r', linestyle='-.')
ax.plot(numpy.arange(1,46) / 1.0, lmaxUp2012, color='pink', linestyle='-.')
ax.plot(numpy.arange(-45,0) / 1.0,maxDown2012, color='b',linestyle='-.')
ax.plot(numpy.arange(-45,0) / 1.0, lmaxDown2012, color='skyblue', linestyle='-.')


ax.set_ylabel("Days")
ax.set_xlabel("Temperature Departure $^{\circ}\mathrm{F}$")
ax.set_title("Ames [1893-2011] Consecuative Days Temperature Streak\nabove or below average temperature")

ax.grid(True)
ax.legend()

fig.savefig("test.ps")
import iemplot
iemplot.makefeature('test')
