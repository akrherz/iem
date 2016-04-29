import matplotlib.pyplot as plt
from pyiem.plot import maue
import datetime
import numpy as np

avgs = np.zeros((24, 53), 'f')
cnts = np.zeros((24, 53), 'f')


def make_y(ts):
    if ts.hour >= 5:
        return ts.hour - 5
    return ts.hour + 19

maxv = 0
for line in open('nexrad35.txt'):
    tokens = line.split(",")
    ts = datetime.datetime.strptime(tokens[0], '%Y%m%d%H%M')
    coverage = float(tokens[1])
    if coverage > maxv:
        print line
        maxv = coverage
    if ts.year > 1007:
        avgs[make_y(ts), int(ts.strftime("%j"))/7-1] += coverage
        cnts[make_y(ts), int(ts.strftime("%j"))/7-1] += 1.0


pixels = 6000 * 2400

(fig, ax) = plt.subplots(1, 1)

cmap = maue()
x, y = np.meshgrid(np.arange(53), np.arange(24))
m = ax.imshow(avgs / cnts / 100. * pixels, aspect='auto',
              interpolation='bicubic',
              cmap=plt.get_cmap("gist_ncar"), extent=[0, 53, 24, 0])
plt.colorbar(m, label='square miles, Iowa = 56,000')
ax.set_ylim(0, 24)
ax.set_yticks((0, 4, 8, 12, 16, 20))
ax.set_xticks(range(0, 55, 7))
ax.set_xticklabels(('Jan 1', 'Feb 19', 'Apr 8', 'May 27', 'Jul 15',
                    'Sep 2', 'Oct 21', 'Dec 9'))
ax.set_yticks(range(0, 24, 4))
ax.set_yticklabels(("Mid", "4 AM", "8 AM", "Noon", "4 PM", "8 PM"))
ax.set_ylabel("Central Daylight Time")

box = ax.get_position()
ax.set_position([box.x0, box.y0,
                 box.width * 0.95, box.height])

ax2 = ax.twinx()
ax2.set_yticks(range(0, 24, 4))
ax2.set_yticklabels(("5", "9", "13", "17", "21", "1"))
ax2.set_ylabel("UTC")
ax2.set_ylim(0, 24)

box = ax2.get_position()
ax2.set_position([box.x0, box.y0,
                  box.width * 0.95, box.height])
# ax.bar(np.arange(1, 366), avgs[:-1] / cnts[:-1]/100. * pixels,fc='b',ec='b')
# ax.set_xticks((1,32,60,91,121,152,182,213,244,274,305,335,365))
# ax.set_xticklabels(calendar.month_abbr[1:])
ax.grid(True, color='white')
# ax.set_xlim(0, 366)
# ax.set_ylabel("Areal Coverage of 35+ dbZ [sq miles], Iowa=56,000")
ax.set_title(("Climatology of 35+ dbZ Returns over CONUS\n"
              "Based on 1996-2015 IEM Composites of NWS NEXRAD"))
ax.set_xlabel("Partitioned by Week of Year, Smoothed")
fig.savefig('test.png')
