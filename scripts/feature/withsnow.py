import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

snowh = []
nosnowh = []
snowl = []
nosnowl = []
for month in [11,12,1,2,3]:
	ccursor.execute("""
	select avg(high), avg(low) from alldata where 
	month = %s and stationid = 'ia0200' and snowd > 0
	""", (month,) )
	row = ccursor.fetchone()
	snowh.append( row[0] )
	snowl.append( row[1] )

	ccursor.execute("""
	select avg(high), avg(low) from alldata where 
	month = %s and stationid = 'ia0200' and snowd = 0
	""", (month,) )
	row = ccursor.fetchone()
	nosnowh.append( row[0] )
	nosnowl.append( row[1] )

import matplotlib.pyplot as plt
import numpy

fig = plt.figure()
ax = fig.add_subplot(211)

def autolabel(rects):
    # attach some text labels
    for rect in rects:
        height = float(rect.get_height())
        ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height),
                ha='center', va='bottom')


ax.set_xlim(-0.5, 4.5)
ax.set_xticklabels( ('','Nov','Dec','Jan','Feb','Mar') )
rects = ax.bar( numpy.arange(5) - 0.4, snowh, 0.4 , label='With Snow Cover')
autolabel(rects)

rects = ax.bar( numpy.arange(5), nosnowh, 0.4, label='No Snow Cover', facecolor='brown')
autolabel(rects)
ax.legend(ncol=2)
ax.grid(True)
ax.set_ylabel('High Temperature $^{\circ}\mathrm{F}$')
ax.set_ylim(20,65)
ax.set_title("Ames Monthly Average Temperature [1964-2009]")

ax = fig.add_subplot(212)

ax.set_xlim(-0.5, 4.5)
ax.set_xticklabels( ('','Nov','Dec','Jan','Feb','Mar') )
rects = ax.bar( numpy.arange(5) - 0.4, snowl, 0.4 , label='With Snow Cover')
autolabel(rects)

rects = ax.bar( numpy.arange(5), nosnowl, 0.4, label='No Snow Cover', facecolor='brown')
autolabel(rects)
ax.legend(ncol=2)
ax.grid(True)
ax.set_ylabel('Low Temperature $^{\circ}\mathrm{F}$')
ax.set_ylim(0,44)

import iemplot
fig.savefig('test.ps')
iemplot.makefeature('test')
