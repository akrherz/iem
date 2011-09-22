import iemdb, numpy
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

final = []
for yr in range(1893,2012):
  ccursor.execute("""SELECT day, high from alldata_ia where stationid = 'ia0200'
  and month = 9 and year = %s and sday < '0919' ORDER by day ASC""", (yr,))
  data = [100.]*5
  minV = 100.
  for row in ccursor:
    if yr == 2011:
      print row
    data.pop()
    data.insert(0, row[1] )
    avg = sum(data) / 5.0
    #avg = max(data)
    if avg < minV:
      minV = avg
  final.append( minV )

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)

bars = ax.bar( numpy.arange(1893,2012)-0.4, final , ec='b', fc='b')
bars[-1].set_edgecolor('r')
bars[-1].set_facecolor('r')
ax.set_xlim(1892.5,2011.5)
ax.set_ylim(55,90)
ax.grid(True)
ax.set_ylabel("Average High Temp $^{\circ}\mathrm{F}$")
ax.set_title("Ames coldest 5 day period in September prior to 19 Sept")

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
