import matplotlib.pyplot as plt
from windrose import WindroseAxes
import math
from matplotlib.patches import Rectangle

drct = []
sped = []
for mo in range(12):
    drct.append([])
    sped.append([])
count = [0]*12
east = [0]*12
for line in open('omaha.txt'):
    tokens = line.split(",")
    if len(tokens) != 3:
        continue
    mo = int(line[4:6]) - 1
    ss = float(tokens[2])
    dd = float(tokens[1])
    if dd >= 45 and dd <= 135:
        east[mo] += 1
    count[mo] += 1
    sped[mo].append( ss )
    drct[mo].append( dd )
print east, count
fig = plt.figure(figsize=(12, 10), dpi=80, facecolor='w', edgecolor='w')
i = 0
months = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT',
          'NOV','DEC']
fig.text(0.5,0.96, "1960-2013 Omaha RAOB 200 hPa Monthly Wind Roses", ha='center', va='top', fontsize=26)
fig.text(0.98,0.01, "Percentages shown are frequency of primarily easterly wind",
     ha='right')
for y in [0.65,0.35,0.05]:
    for x in [0.02,0.27,0.52,0.77]:
        ax = WindroseAxes(fig, [x,y,0.21,0.28], axisbg='w')
        fig.add_axes(ax)
        ax.bar(drct[i], sped[i], normed=True, bins=[0,1,20,40,60,80,100,200], 
           opening=0.8, edgecolor='white', nsector=16, rmax=30.0)
        ax.text(0.5,0.25, "%s\n%.1f%%" % (months[i],
		east[i] / float(count[i]) * 100.0), transform=ax.transAxes, fontsize=26)
        i += 1

handles = []
for p in ax.patches_list:
    color = p.get_facecolor()
    handles.append( Rectangle((0, 0), 0.1, 0.3,
                    facecolor=color, edgecolor='black'))

l = fig.legend( handles, ['0-20','20-40','40-60','60-80', '80-100','100+'] , 
     loc=3,
     ncol=6, title='Wind Speed [%s]' % ('mph',),
     mode=None, columnspacing=0.9, handletextpad=0.45)

plt.setp(l.get_texts(), fontsize=10)

plt.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
