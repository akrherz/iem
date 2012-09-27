import iemdb, network
import numpy

COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
select year, min(extract(doy from day)) from alldata_ia where station = 'IA2203' and high < 70 and month > 6 GROUP by year ORDER by year

""")
years = []
doy = []
for row in ccursor:
    years.append( row[0] )
    doy.append( float(row[1])  )
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

ax.set_title("First Day with High Temperature below 70$^{\circ}\mathrm{F}$\nfor Des Moines after 1 July (1880-2012)")
ax.grid(True)
ax.set_ylabel('First Date')
ax.set_xlim(1889.5,2013.5)
ax.set_xlabel("years in red were later than 2012")
ax.set_yticks( (1,32,60,91,121,152,182,188,195,202,213,220,227,233,244,251,258,265,274,305,335,365) )
ax.set_yticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul 1','Jul 8', 'Jul 15', 'Jul 22', 'Aug 1','Aug 8', 'Aug 15', 'Aug 22', 'Sep 1','Sep 8', 'Sep 15', 'Sep 22', 'Oct','Nov','Dec') )
ax.set_ylim(182,275)
#ax.legend(loc='best')


fig.savefig('test.ps')
iemplot.makefeature('test')
