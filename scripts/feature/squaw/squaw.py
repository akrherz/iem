""" Accumulate PET for this year and previous ones """
import iemdb
ISUAG = iemdb.connect('squaw', bypass=True)
icursor = ISUAG.cursor()
import numpy.ma

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1, 1)

for yr in range(1991, 2013):
    icursor.execute("""SELECT extract(doy from valid) as d, max(cfs) from real_flow
    WHERE extract(year from valid) = %s 
    GROUP by d ORDER by d ASC""" % (yr, ))
    obs = numpy.ma.zeros( (366,), 'f')
    for row in icursor:
        obs[ row[0] - 1] = row[1]
    
    if yr in [2010, 2012,  1993]:
        ax.plot(range(1,367), obs, linewidth=2, label=yr, zorder=2)
    else:
        ax.plot(range(1,367), obs, color='tan', zorder=1)

ax.plot([1,366],[3700,3700], label='Flood')
ax.legend(loc='best', ncol=5)
ax.set_title("Ames Squaw Creek at Lincoln Way (1991-2012)")
ax.set_ylabel("Water Flow [cfs], log scale")
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlim(0,366)
ax.set_yscale('log')
ax.grid(True)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
