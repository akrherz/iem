import iemdb
import numpy
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

yearly = []
for yr in range(1893,2012):
  ccursor.execute("""
  SELECT day, precip from alldata where year = %s and stationid = 'ia0200'
  and month in (7,8) ORDER by day ASC
  """ % (yr,))
  maxRunning = 0
  running = 0
  for row in ccursor:
    if row[1] >= 0.25:
      if running > maxRunning:
        maxRunning = running
      running = 0
    else:
      running += 1
  if running > maxRunning:
    maxRunning = running
  yearly.append( maxRunning )

yearly = numpy.array( yearly )

yearly5 = []
for yr in range(1893,2012):
  ccursor.execute("""
  SELECT day, precip from alldata where year = %s and stationid = 'ia0200'
  and month in (7,8) ORDER by day ASC
  """ % (yr,))
  maxRunning = 0
  running = 0
  for row in ccursor:
    if row[1] >= 0.5:
      if running > maxRunning:
        maxRunning = running
      running = 0
    else:
      running += 1
  if running > maxRunning:
    maxRunning = running
  yearly5.append( maxRunning )

yearly5 = numpy.array( yearly5 )


import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(211)

avgV = numpy.average(yearly)
bars = ax.bar(numpy.arange(1893,2012)-0.4, yearly, fc='r', ec='r')
for bar in bars:
  if bar.get_height() < avgV:
    bar.set_facecolor('b')
    bar.set_edgecolor('b')
ax.plot([1892,2012],[avgV,avgV], color='black')
ax.set_xlim(1892.5,2011.5)
ax.grid(True)
ax.set_ylabel("Days")
ax.set_title("Ames Maximum Period in July & August (1893-2011)\nBetween Daily 0.25+ inch Rainfalls")

ax2 = fig.add_subplot(212)
ax2.set_title("Between Daily 0.50+ inch Rainfalls")
avgV = numpy.average(yearly5)
bars = ax2.bar(numpy.arange(1893,2012)-0.4, yearly5, fc='r', ec='r')
for bar in bars:
  if bar.get_height() < avgV:
    bar.set_facecolor('b')
    bar.set_edgecolor('b')
ax2.plot([1892,2012],[avgV,avgV], color='black')
ax2.set_xlim(1892.5,2011.5)
ax2.grid(True)
ax2.set_ylabel("Days")


ax2.set_xlabel("*2011 thru 8 August 2011")
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')

