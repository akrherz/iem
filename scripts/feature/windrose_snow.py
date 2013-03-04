import matplotlib.pyplot as plt
from windrose.windrose import WindroseAxes
from matplotlib.patches import Rectangle

import iemdb
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

sped = []
drct = []
acursor.execute("""
 SELECT drct, sknt from alldata where station = 'DSM' and 
 presentwx ~* 'SN' and sknt > 0 and drct >= 0 and drct < 360 
""")
for row in acursor:
    sped.append( row[1] * 1.15)
    drct.append( row[0] )
    

fig = plt.figure(figsize=(6, 7), dpi=80, facecolor='w', edgecolor='w')
rect = [0.1, 0.1, 0.8, 0.8]
ax = WindroseAxes(fig, rect, axisbg='w')
fig.add_axes(ax)
ax.bar(drct, sped, normed=True, bins=[0,2,5,7,10,15,20], opening=0.8, 
       edgecolor='white', nsector=18)
handles = []
for p in ax.patches_list:
    color = p.get_facecolor()
    handles.append( Rectangle((0, 0), 0.1, 0.3,
                facecolor=color, edgecolor='black'))
l = fig.legend( handles, ('2-5','5-7','7-10','10-15','15-20','20+') , loc=3,
 ncol=6, title='Wind Speed [%s]' % ('mph',), 
 mode=None, columnspacing=0.9, handletextpad=0.45)
plt.setp(l.get_texts(), fontsize=10)

plt.gcf().text(0.5,0.91, "1960-2012 Des Moines Airport Wind Rose\nWhen observation includes falling snow", 
               fontsize=16, ha='center')
plt.gcf().text(0.01,0.1, "Generated: 4 March 2013" ,
                   verticalalignment="bottom")

plt.savefig('test.ps')
import iemplot
iemplot.makefeature('test')