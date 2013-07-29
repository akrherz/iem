import matplotlib.pyplot as plt
from windrose.windrose import WindroseAxes
import math
from matplotlib.patches import Rectangle

def calc_drct(u,v):
    if (v > 0):
        return ((180 / math.pi) * math.atan(u/v) + 180)
    if (u < 0 and v < 0):
        return ((180 / math.pi) * math.atan(u/v) + 0)
    if (u > 0.0 and v < 0.0):
        return ((180 / math.pi) * math.atan(u/v) + 360)
    return 0

drct = []
sped = []
for line in open('dsm.txt'):
    tokens = line.split(",")
    if len(tokens) != 6:
        continue
    if line[5:7] != '07':  # JUL ONLY!
        continue
    u = float(tokens[4])
    v = float(tokens[5])
    ss = ((u*u) + (v*v))**.5 * 2.23694
    dd = calc_drct(u,v)
    if u < 0:
        print line.strip(), ss, dd
    sped.append( ss )
    drct.append( dd )

fig = plt.figure(figsize=(6, 7), dpi=80, facecolor='w', edgecolor='w')
rect = [0.1, 0.1, 0.8, 0.8]
ax = WindroseAxes(fig, rect, axisbg='w')
fig.add_axes(ax)
ax.bar(drct, sped, normed=True, bins=[0,20,30,40,50,75,200], opening=0.8,
           edgecolor='white', nsector=16)

handles = []
for p in ax.patches_list:
    color = p.get_facecolor()
    handles.append( Rectangle((0, 0), 0.1, 0.3,
                    facecolor=color, edgecolor='black'))
l = fig.legend( handles, ['0-20','20-30','30-40','40-50', '50-75','75+'] , loc=3,
     ncol=6, title='Wind Speed [%s]' % ('mph',),
     mode=None, columnspacing=0.9, handletextpad=0.45)
plt.setp(l.get_texts(), fontsize=10)

plt.savefig('test.png')
