import matplotlib.pyplot as plt
import Image
import matplotlib.patheffects as PathEffects

sunrises = 2338.
sunsets = 2334.

rise_hits = 0
rise_cases = 0
set_hits = 0
set_cases = 0
for line in open('results.txt'):
    tokens = line.strip().split(",")
    if tokens[0] == 'RISE':
        rise_cases += 1.0
        if tokens[3] == '1':
            rise_hits += 1.0
    elif tokens[0] == 'SET':
        set_cases += 1.0
        if tokens[3] == '1':
            set_hits += 1.0

(fig, ax) = plt.subplots(1,1)

data = Image.open('max.jpg')
ax.imshow(data, extent=(0,3,0,2), zorder=2)

bars = ax.bar([0.2, 1.2, 2.2], [rise_hits / rise_cases  * 2.0, set_hits / set_cases * 2.0,
                                0.246 * 2], width=0.6, zorder=3)
for i, bar in enumerate(bars):
    txt = ax.text(i+0.5, bar.get_height()+0.05, "%.1f%%" % (bar.get_height() / 2.0 * 100.0,), zorder=4,
                  ha='center', fontsize=20, color='yellow')
    txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                 foreground="k")])

ax.set_xticks([0.5,1.5,2.5])
ax.set_xticklabels(['Red Sky @ Morning\n%.0f/%.0f %.0f' % (rise_hits, rise_cases, sunrises), 
                    'Red Sky @ Night\n%.0f/%.0f %.0f' % (set_hits, set_cases, sunsets), 'All Days'])
ax.set_ylabel("Precip Frequency for 24 hour period after")
ax.set_yticks([])

txt = ax.text(1.5, 1.5, "Does a Red Sky predict Precipitation?\n2006-2013 Ames/Nevada Webcam Analysis",
              color='k', fontsize=20, ha='center')
txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                 foreground="white")])
fig.savefig('test.png')
