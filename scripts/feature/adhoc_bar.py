import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patheffects as PathEffects

(fig, ax) = plt.subplots(1,1)

one = [1.02, 0.98, 2.36, 2.26] # 2013
two = [0.42, 0.93, 0.72, 1.67] # 1947
three = [1.24, 2.32, 0.98, 2.09] # 2012

labels = ['4 Oct - 2.23"', '13 Oct - 2.09"','30 Oct - 1.67"']

bars = ax.bar(np.arange(1,5)-0.45, one, width=0.3, label='2013', fc='r', alpha=0.5)
bars[-2].set_alpha(1)
for i, bar in enumerate(bars[:-1]):
    txt = ax.text( bar.get_x()+0.15, 0.15, '%s"' % (one[i],), rotation=90, va='bottom',
                   ha='center')
    txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground="w")])
bars = ax.bar(np.arange(1,5)-0.15, three, width=0.3, label='2012', fc='g', alpha=0.5)
bars[-3].set_alpha(1)
for i, bar in enumerate(bars[:-1]):
    txt = ax.text( bar.get_x()+0.15, 0.15, '%s"' % (three[i],), rotation=90, va='bottom',
                   ha='center')
    txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground="w")])
bars = ax.bar(np.arange(1,5)+0.15, two, width=0.3, label='1947', fc='b', alpha=0.5)
bars[-1].set_alpha(1)
for i, bar in enumerate(bars[:-1]):
    txt = ax.text( bar.get_x()+0.15, 0.15, '%s"' % (two[i],), rotation=90, va='bottom',
                   ha='center')
    txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground="w")])

txt = ax.text(3.7, 0.15, labels[0], rotation=90, va='bottom', ha='center')
txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground="w")])
txt = ax.text(4.0, 0.15, labels[1], rotation=90, va='bottom', ha='center')
txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground="w")])
txt = ax.text(4.3, 0.15, labels[2], rotation=90, va='bottom', ha='center')
txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground="w")])

ax.set_title("Des Moines Jul,Aug,Sep Monthly Precip Totals\nand maximum daily precipitation in October")
ax.set_xticks(np.arange(1,5))
ax.set_xticklabels(['July\nTotal', 'August\nTotal', 'September\nTotal', 'October\n1 Day Max'])
ax.grid(True)
ax.legend(loc='best')
ax.set_ylabel("Precipitation [inch]")
ax.set_xlabel("* 2013 thru 4 October")

fig.savefig('131005.png')
#import iemplot
#iemplot.makefeature('test')