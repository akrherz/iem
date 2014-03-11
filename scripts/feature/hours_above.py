import psycopg2
import math
ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
acursor = ASOS.cursor()


data = []
years = []
    # Query out obs
acursor.execute("""
select extract(year from valid + '4 months'::interval) as yr, sum(valid - lag) from (select valid, lag(valid) OVER (ORDER by valid ASC), tmpf from alldata where station = 'LSE') as foo WHERE tmpf < -0.49 GROUP by yr ORDER by yr ASC
""")
for row in acursor:
    data.append( (row[1].days * 86400. + row[1].seconds) / 3600.0 )
    years.append( float(row[0]) )

import matplotlib.pyplot as plt
import numpy as np

years = np.array(years)
data = np.array(data)

fig, ax = plt.subplots(1,1)

ax.set_title("Dubuque Airport Hours Below 0$^\circ$F [1950-2014]\nbased on Iowa Environmental Mesonet Unofficial METAR Archives")
ax.set_xlabel("year of spring shown, *2014 thru 25 Feb")
bars = ax.bar( years-0.4, data / 24.0, facecolor='r', edgecolor='r')
for i,bar in enumerate(bars):
    if data[i] >= data[-1]:
        bar.set_facecolor('b')
        bar.set_edgecolor('b')
ax.set_ylabel("Hours Below 0$^{\circ}F$ (expressed in days)")
ax.set_xlim(1949.5,2014.5)
#ax.set_ylim(0,21)
ax.grid(True)


fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
