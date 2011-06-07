import iemdb

COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
ccursor2 = COOP.cursor()

years = []
highs = []
snow = []
ccursor.execute("""SELECT year, max(day) from alldata WHERE month < 6
  and snow >= 1 and stationid = 'ia2203' and year < 2011 GROUP by year ORDER by year ASC""")
for row in ccursor:
  ccursor2.execute("""SELECT max(high) from alldata WHERE day < %s
  and day > (%s - '7 days'::interval) and stationid = 'ia2203' and year = %s""", (row[1], row[1], row[0]))
  row2 = ccursor2.fetchone()
  highs.append( float(row2[0]) )
  years.append( float(row[0]) )
  ccursor2.execute("""SELECT snow from alldata WHERE day = %s
  and stationid = 'ia2203'""", (row[1],))
  row2 = ccursor2.fetchone()
  snow.append( float(row2[0]) * 35)


import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111)

ax.scatter(years, highs, s=snow)

ax.grid(True)
ax.set_xlim(1892,2011)
ax.set_title("Des Moines Last Spring Daily Snowfall >= 1 inch\nMax Temperature for week before")
ax.set_ylabel("Maximum Temperature $^{\circ}\mathrm{F}$")
ax.set_xlabel("Year, size of dot is relative snowfall amount (max %.0f inches)" % (max(snow) / 35. ,))
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
