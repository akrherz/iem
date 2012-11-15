import iemdb, network
import numpy
import mx.DateTime

COOP = iemdb.connect('asos', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
 select extract(year from valid) as yr, max(valid) from alldata 
 WHERE station = 'DSM' and dwpf >= 64.9 GROUP by yr ORDER by yr ASC
""")
years = []
doy = []
for row in ccursor:
    years.append( row[0] )
    doy.append( int(row[1].strftime("%j"))  )
#    total.append( float(row[1] + row[2])  )

years = numpy.array(years)

import matplotlib.pyplot as plt
import iemplot
import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=12)

fig, ax = plt.subplots(1,1)
bars = ax.bar( years - 0.4, doy, 
        facecolor='purple', ec='purple', zorder=1, label='After 19 Aug')
for bar in bars:
    if bar.get_height() > bars[-1].get_height():
        bar.set_facecolor('r')
        bar.set_edgecolor('r')

ax.set_title("Date of last 65+$^{\circ}\mathrm{F}$ dew point for the year\nfor Des Moines (1932-2012)")
ax.grid(True)
ax.set_ylabel('Last Date of Year')
ax.set_xlim(1932.5,2013.5)
ax.set_xlabel("1934, 2004 are only years later than 2012")
#ax.set_yticks( (1,32,60,91,121,152,182,188,195,202,213,220,227,233,244,251,258,265,274,305,335,365) )
#ax.set_yticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul 1','Jul 8', 'Jul 15', 'Jul 22', 'Aug 1','Aug 8', 'Aug 15', 'Aug 22', 'Sep 1','Sep 8', 'Sep 15', 'Sep 22', 'Oct 1','Nov','Dec') )
sts = mx.DateTime.DateTime(2000,8,1)
ets = mx.DateTime.DateTime(2000,11,1)
interval = mx.DateTime.RelativeDateTime(days=1)
now = sts
yticks = []
yticklabels = []
while now < ets:
    if now.day in [1,8,15,22,29]:
        yticks.append( int(now.strftime("%j")))
        yticklabels.append( now.strftime("%b %-d"))
    now += interval
ax.set_yticks(yticks)
ax.set_yticklabels(yticklabels)
ax.set_ylim(min(yticks),max(yticks)+1)
#ax.legend(loc='best')


fig.savefig('test.ps')
iemplot.makefeature('test')
