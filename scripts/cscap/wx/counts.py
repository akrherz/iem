import psycopg2
import sys
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mpcolors
import matplotlib.cm as cm

MODEL = sys.argv[1]
SCENARIO = sys.argv[2]

pgconn = psycopg2.connect(database='coop')
cursor = pgconn.cursor()

cursor.execute("""SELECT station, extract(year from day) as yr, count(*)
 from hayhoe_daily WHERE high is not null and low is not null 
 and precip is not null and model = %s and scenario = %s
 GROUP by station, yr""", (MODEL, SCENARIO))

data = {}
for row in cursor:
    station = row[0]
    year = int(row[1])
    count = row[2]
    
    if not data.has_key(station):
        data[station] = np.zeros((140,))
    data[station][year-1960] = count
    

stations = data.keys()
stations.sort()

counts = np.zeros((len(stations), 140))
for i, station in enumerate(stations):
    counts[i, :] = data[station]

(fig, ax) = plt.subplots(1,1)

cmap = cm.get_cmap('BrBG')
cmap.set_over("white")
cmap.set_under("black")
norm = mpcolors.BoundaryNorm([180,300,360,365,366,367,368,400], cmap.N)


res = ax.pcolormesh(np.arange(1960,2100), np.arange(len(stations)+1), counts,
                    norm=norm, cmap=cmap)
fig.colorbar(res)
ax.set_yticks(np.arange(len(stations))+0.5)
ax.set_yticklabels(stations)
ax.set_xticklabels(np.arange(1960,2101,20))
ax.set_xlim(1960,2100)
ax.set_ylim(0, len(stations))
ax.grid(True)

fig.savefig('test.png')