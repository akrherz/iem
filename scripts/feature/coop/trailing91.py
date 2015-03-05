import psycopg2
import numpy as np
pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = pgconn.cursor()
import datetime

cursor.execute("""select day, avg((high+low)/2.) OVER (ORDER by day ASC ROWS BETWEEN 91 PRECEDING AND CURRENT ROW) from alldata_ia where station = 'IA0200' and year > 2013 ORDER by day ASC""")

x = []
y = []
for row in cursor:
    x.append(row[0])
    y.append(row[1])

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
(fig, ax) = plt.subplots(1, 1)

ax.bar(x,y)
ax.set_xlim(datetime.date(2015, 2, 15), datetime.date(2015, 3, 5))
ax.set_ylim(20.5,23)
ax.set_yticks(np.arange(20.5, 23, 0.25))
ax.set_title("Ames Trailing 91 Day Average Temperature (Feb/Mar 2015)")
ax.set_ylabel("Average Temperature $^\circ$F")
ax.xaxis.set_major_formatter(mdates.DateFormatter('%-d\n%b'))
ax.grid(True)

fig.savefig('150305.png')
