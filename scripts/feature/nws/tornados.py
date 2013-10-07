import numpy as np
import matplotlib.pyplot as plt

d2013 = [0, 0, 0, 0, 
         8, 7, 0, 0,
         0, 5, 0, 0]

montotal = np.zeros( (12,))
d2012 = np.zeros( (12,))

for line in open('1950-2012_torn.csv'):
    tokens = line.split(",")
    if tokens[7] != 'IA':
        continue
    montotal[ int(tokens[2]) - 1] += 1
    if int(tokens[1]) == 2012:
        d2012[ int(tokens[2]) - 1] += 1
        
spc = montotal / 63.0

cogil = np.array([0,0,70,212,379,467,194,103,56,13,22,1], 'f') / 32.0

(fig, ax) = plt.subplots(1,1)

bars = ax.bar(np.arange(1,13)-0.4, cogil, width=0.8, zorder=1, label='1980-2011 Avg')
for i, bar in enumerate(bars):
    ax.text(bar.get_x()+0.4, cogil[i]+0.4, "%.1f" % (cogil[i],), ha='center')
bars = ax.bar(np.arange(1,13)-0.35, d2012, width=0.3, zorder=2, fc='yellow',
              label='2012')
for i, bar in enumerate(bars):
    if d2012[i] == 0:
        continue
    ax.text(bar.get_x()+0.1, d2012[i]-0.6, "%.0f" % (d2012[i],), ha='center')

bars = ax.bar(np.arange(1,13)+0.05, d2013, width=0.3, zorder=2, fc='red',
              label='2013')
for i, bar in enumerate(bars):
    if d2013[i] == 0:
        continue
    ax.text(bar.get_x()+0.1, d2013[i]-0.6, "%.0f" % (d2013[i],), ha='center')

ax.set_title("Iowa Tornado Reports by Month")
ax.set_ylabel("Count")
ax.set_xlim(0.5,12.5)
ax.set_xticks(np.arange(1,13))
ax.set_xlabel("*2013 preliminary thru 6 October")
ax.grid(True)
ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul',
                    'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
ax.legend()
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')