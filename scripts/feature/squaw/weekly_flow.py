import psycopg2
import matplotlib.pyplot as plt
import numpy as np
from pyiem.plot import james
import matplotlib.colors as mpcolors

SQUAW = psycopg2.connect(database='squaw', host='iemdb', user='nobody')
cursor = SQUAW.cursor()

data = np.ma.ones((26, 53), 'f') * -99.0
data.mask = np.where(data < 0, True, False)
cursor.execute("""
  SELECT extract(year from valid) as yr, extract(week from valid) as week,
  avg(cfs) from real_flow GROUP by yr, week

""")

for row in cursor:
    data[row[0] - 1990, row[1] - 1] = row[2]

levels = np.percentile(np.where(data < 0, 0, data),
                       [10, 20, 30, 40, 50, 60, 70, 80, 90, 99])
norm = mpcolors.BoundaryNorm(levels, 12)

cmap = james()
cmap.set_under("#FFFFFF")
(fig, ax) = plt.subplots(1, 1)
res = ax.imshow(np.flipud(data), interpolation='nearest',
                extent=(1, 54, 1989.5, 2015.5), cmap=cmap,
                norm=norm, aspect='auto')
ax.set_xticks(np.arange(1, 56, 7))
ax.set_xlim(1, 53)
ax.set_xticklabels(('Jan 1', 'Feb 19', 'Apr 8', 'May 27', 'Jul 15',
                    'Sep 2', 'Oct 21', 'Dec 9'))
ax.grid()
ax.set_title("Squaw Creek @ Lincoln Way in Ames\nWeekly Average Streamflow")
ax.set_ylabel("Year")
ax.set_xlabel("Day of Year")
fig.colorbar(res, extend='both', label='Cubic Feet per Second')
fig.savefig('test.png')
