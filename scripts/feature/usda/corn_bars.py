import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mpcolors
import datetime
from matplotlib.colors import rgb2hex
import matplotlib.patheffects as PathEffects

cmap = plt.get_cmap('jet')
cmap.set_over('black')
cmap.set_under('white')
bins = np.arange(0, 0.71, .05)
bins[0] = 0.01
norm = mpcolors.BoundaryNorm(bins, cmap.N)

df = pd.read_csv('corn.csv')
df.sort('Week Ending')


(fig, ax) = plt.subplots(1, 1)

last = 0
yearmax = [0]*(2016-1979)
for (i, row) in df.iterrows():
    delta = row['Value'] - last
    if delta < 0:
        delta = row['Value']
    last = row['Value']
    ts = datetime.datetime.strptime(row['Week Ending'], '%Y-%m-%d')
    jday = int(ts.strftime("%j"))
    yearmax[ts.year-1979] = max(yearmax[ts.year-1979], delta)
    val = delta / 100.
    ax.bar(jday-7, 1, bottom=ts.year-0.5, width=7, ec='None',
           fc=cmap(norm([val]))[0])
    print ts.year, jday, delta

sts = datetime.datetime(2000,4,1)
ets = datetime.datetime(2000,6,25)
now = sts
interval = datetime.timedelta(days=1)
jdays = []
labels = []
while now < ets:
    if now.day in [1, 8, 15, 22, 29]:
        fmt = "%-d\n%b" if now.day == 1 else "%-d"
        jdays.append(int(now.strftime("%j")))
        labels.append(now.strftime(fmt))
    now += interval

ax.set_xticks(jdays)
ax.set_xticklabels(labels)

ax.set_yticks(range(1979,2016))
ylabels = []
for yr in range(1979,2016):
    if yr % 5 == 0:
        ylabels.append("%s %s" % (yr, yearmax[yr-1979]))
    else:
        ylabels.append("%s" % (yearmax[yr-1979],))
ax.set_yticklabels(ylabels, fontsize=10)

ax.set_ylim(1978.5, 2015.5)
ax.set_xlim(min(jdays), max(jdays))
ax.grid(True)
ax.set_title("USDA NASS Weekly Corn Planting Progress, till 3 May 2015\nIowa % acres planted over seven day period, year max labelled")

ax2 = plt.axes([0.92, 0.1, 0.07, 0.8], frameon=False,
               yticks=[], xticks=[])
colors = []
for i in range(len(bins)):
    colors.append(rgb2hex(cmap(i)))
    txt = ax2.text(0.5, i, "%.0f" % (bins[i]*100.,), ha='center', va='center',
                  color='w')
    txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                             foreground="k")])
ax2.barh(np.arange(len(bins)), [1]*len(bins), height=1,
         color=cmap(norm(bins)),
         ec='None')


fig.savefig('test.png')
