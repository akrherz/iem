import iemdb
import numpy
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
SELECT year, count(*) from alldata where 
stationid in (SELECT lower(id) from stations where network = 'IACLIMATE') and
precip >= 4 and year > 1950 GROUP by year ORDER by year ASC
""")

data = {}
for row in ccursor:
    data[row[0]] = row[1]
    
yearly = []
for yr in range(1951,2011):
    yearly.append( data.get(yr,0) )

yearly = numpy.array(yearly)
avg = numpy.average(yearly)

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)

bars = ax.bar(numpy.arange(1951,2011) - 0.3, yearly)
for bar in bars:
    if bar.get_height() > avg:
        bar.set_facecolor('r')
ax.set_xlim(1950.5, 2010.5)
ax.set_title("Iowa 4+ inch Daily Rainfall Reports\nbased on 105 long term sites [1951-2010]")
ax.set_ylabel("Reports (red bars above average: %.0f)" % (avg,))
ax.grid(True)
fig.savefig('test.png')