import psycopg2
import numpy as np
import numpy.ma as ma
import datetime

def run():
    ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
    acursor = ASOS.cursor()

    acursor.execute("""
     select extract(doy from valid), 
     greatest(skyl1, skyl2, skyl3, skyl4) as sky from alldata 
     WHERE station = 'DSM' and 
     (skyc1 = 'OVC' or skyc2 = 'OVC' or skyc3 = 'OVC' or skyc4 = 'OVC')
     and valid > '1973-01-01' and (extract(minute from valid) = 0 or
     extract(minute from valid) > 50)
    """)
    
    doys = []
    levels = []
    for row in acursor:
        if row[1] is None:
            continue
        doys.append( row[0] )
        levels.append( row[1] )
        
    return doys, levels

doys, levels = run()

w = np.arange(1,366,7)
z = np.array([  100,   200,   300,   400,   500,   600,   700,   800,   900,
        1000,  1100,  1200,  1300,  1400,  1500,  1600,  1700,  1800,
        1900,  2000,  2100,  2200,  2300,  2400,  2500,  2600,  2700,
        2800,  2900,  3000,  3100,  3200,  3300,  3400,  3500,  3600,
        3700,  3800,  3900,  4000,  4100,  4200,  4300,  4400,  4500,
        4600,  4700,  4800,  4900,  5000,  5500,  6000,  6500,  7000,
        7500,  8000,  8500,  9000,  9500, 10000, 11000, 12000, 13000,
       14000, 15000, 16000, 17000, 18000, 19000, 20000, 21000, 22000,
       23000, 24000, 25000, 26000, 27000, 28000, 29000, 30000, 31000])

H, yedges, xedges = np.histogram2d(levels, doys, 
                                    bins=(z, w) )

print len(w), w[-1]

print np.max(H)
H = ma.array(H)
H.mask = np.where( H < 1, True, False)

extent = [xedges[0], xedges[-1], yedges[-1], yedges[0]]

import matplotlib.pyplot as plt
import matplotlib.colors as mpcolors
import matplotlib.cm as cm

(fig, ax) = plt.subplots(1,1)

bounds = np.arange(0,1.2,0.1)
bounds = np.concatenate((bounds, np.arange(1.2,2.2,0.2)))
cmap = cm.get_cmap('jet')
#cmap.set_over('0.25')
cmap.set_under('#F9CCCC')
norm = mpcolors.BoundaryNorm(bounds, cmap.N)


c = ax.imshow(H / 40., aspect='auto', interpolation='nearest', norm=norm)
ax.set_ylim(-0.5,len(z)-0.5)
idx = [0, 4, 9, 19, 29, 39, 49, 54, 59, 64, 69, 74, 79]
ax.set_yticks( idx )
ax.set_yticklabels( z[idx])
ax.set_title("1973-2013 Des Moines Ceilings Frequency\nLevel at which Overcast Conditions Reported")
ax.set_ylabel("Overcast Level [ft AGL], irregular scale")
ax.set_xlabel("Week of the Year")
ax.set_xticks( np.arange(0,55,7) )
ax.set_xticklabels( ('Jan 1', 'Feb 19', 'Apr 8', 'May 27', 'Jul 15', 'Sep 2', 'Oct 21', 'Dec 9'))
b = fig.colorbar(c)
b.set_label("Hourly Obs per week per year")

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')