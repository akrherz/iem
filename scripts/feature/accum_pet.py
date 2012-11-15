""" Accumulate PET for this year and previous ones """
import iemdb
ISUAG = iemdb.connect('isuag', bypass=True)
icursor = ISUAG.cursor()

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1, 1)

for yr in range(1987, 2013):
    icursor.execute("""SELECT extract(doy from valid), c70 from daily
    WHERE station = 'A130209' and extract(year from valid) = %s 
    and extract(month from valid) > 4
    ORDER by valid ASC""" % (yr, ))
    doy = [0]
    c70 = [0]
    for row in icursor:
        doy.append( row[0] )
        c70.append( c70[-1] + row[1] )
    
    if yr in [1988, 2012, 2009, 1993]:
        ax.plot(doy, c70, linewidth=2, label=yr, zorder=2)
    else:
        ax.plot(doy, c70, color='tan', zorder=1)
ax.legend(loc='best')
ax.set_title("Ames Accumulated Potential Evapo-Transpiration (alfalfa)")
ax.set_ylabel("Potential Evapo-transpiration [inch]")
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlim(120,306)
ax.grid(True)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')