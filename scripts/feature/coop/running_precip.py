import iemdb
import datetime
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""SELECT day, precip from alldata_ia
 where station = 'IA0000' and day >= '2011-01-01' ORDER by day ASC""")

data = []
days = []
seven = [0]*7
for row in ccursor:
    seven.pop()
    seven.insert(0, row[1])
    data.append( sum(seven) )
    days.append( row[0])

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

(fig, ax) = plt.subplots(1,1)

ax.fill_between(days, 0, data)
ax.set_xlim( days[0], days[-1] + datetime.timedelta(days=14))
ax.set_title("Iowa Seven Day Statewide Precipitation")
ax.set_ylabel("Precipitation [inch]")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
ax.grid(True)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')