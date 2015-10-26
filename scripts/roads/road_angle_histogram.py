import psycopg2
from shapely.wkb import loads
import math
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
cursor = pgconn.cursor()

cursor.execute("""SELECT geom from roads_base""")


def makedir(u, v):
    if (v == 0):
        v = 0.000000001
    dd = math.atan(u / v)
    ddir = (dd * 180.00) / math.pi

    if (u > 0 and v > 0):  # First Quad
        ddir = 180 + ddir
    elif (u > 0 and v < 0):  # Second Quad
        ddir = 360 + ddir
    elif (u < 0 and v < 0):  # Third Quad
        ddir = ddir
    elif (u < 0 and v > 0):  # Fourth Quad
        ddir = 180 + ddir

    d = int(math.fabs(ddir))
    if d >= 180:
        d -= 180

    return d

weights = []
drcts = []
for row in cursor:
    if row[0] is None:
        continue
    geom = loads(row[0].decode('hex'))
    for line in geom:
        (x, y) = line.xy
        for i in range(len(x)-1):
            dist = ((x[i+1]-x[i])**2 + (y[i+1]-y[i])**2)**.5
            weights.append(dist)
            drcts.append(makedir(x[i+1]-x[i], y[i+1]-y[i]))

(fig, ax) = plt.subplots(1, 1)

ax.hist(drcts, range(0, 181, 5), weights=weights, normed=True)
ax.set_xlabel("Road Orientation")
ax.set_xticks([0, 45, 90, 135])
ax.set_xticklabels(["N-S", "NE_SW", "E-W", "NW-SE", "N-S"])
ax.grid(True)
ax.set_ylabel("Normalized Frequency")
ax.set_title(("Orientation of Primary Iowa Roadways\n(based on Interstates, "
              "US Highways, and some IA Highways)"))

fig.savefig('140922.png')
