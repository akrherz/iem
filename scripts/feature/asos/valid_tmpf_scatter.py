import psycopg2
import datetime
ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
cursor = ASOS.cursor()

cursor.execute("""
 SELECT valid, tmpf from t2014 where station = 'AMW' and p01i > 0 ORDER
 by valid ASC
""")
valid = []
tmpf = []
for row in cursor:
    tmpf.append( row[1] )
    valid.append( row[0] )

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

(fig, ax) = plt.subplots(1,1)

ax.scatter(valid, tmpf, edgecolor='b', marker='s', facecolor='b')
ax.xaxis.set_major_formatter(mdates.DateFormatter('%-d %b'))
ax.grid(True)
ax.set_title("2014 Ames Air Temperature when Precipitation was Reported")
ax.set_ylabel("Temperature $^\circ$F")
ax.set_xlabel("thru 27 March")
ax.set_xlim(left=datetime.datetime(2014,1,1))
ax.axhline(32, color='r')

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
