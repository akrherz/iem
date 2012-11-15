import iemdb
import numpy
from scipy import stats
import mx.DateTime
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

doy = []
years = []
ccursor.execute("""
select year, min(case when high < 32 then sday else '1232' end) from alldata_ia where station = 'IA1319' and month > 7 GROUP by year ORDER by year
""")
for row in ccursor:
    ts = mx.DateTime.strptime("2000%s" % (row[1],), '%Y%m%d')
    doy.append( int(ts.strftime("%j")) )
    years.append( row[0] )
years= numpy.array( years )
doy = numpy.array( doy )
    
ccursor.execute("""
 select extract(year from day - '120 days'::interval) as yr, avg((high+low)/2.0) 
 from alldata_ia where station = 'IA1319' and month in (12,1,2) 
 GROUP by yr ORDER by yr
""")
avgt = []
for row in ccursor:
    avgt.append( float( row[1] ))
    
avgt = numpy.array(avgt)
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(2, 1)

bars = ax[0].bar(years - 0.4, doy, fc='r', ec='r')
for bar in bars:
    if bar.get_height() <= bars[-1].get_height():
        bar.set_facecolor('b')
        bar.set_edgecolor('b')
ax[0].set_title("1893-2012 Cedar Rapids Date of First Frozen Day\nand Average Winter Season Temperature vs First Frozen Day")
ax[0].set_xlim(1892.5, 2012.5)
ax[0].grid(True)
ax[0].set_yticks( (295, 305, 312, 319, 326, 335, 342, 349, 356) )
ax[0].set_yticklabels( ('Oct 22', 'Nov 1', 'Nov 8', 'Nov 15', 'Nov 22', 'Dec 1', 'Dec 8', 'Dec 15', 'Dec 22') )
ax[0].set_ylim(290,366)

h_slope, intercept, r_value, p_value, std_err = stats.linregress(doy, avgt)
y1 = 290 * h_slope + intercept
y2 = 366 * h_slope + intercept
ax[1].plot([290,366], [y1,y2])
ax[1].text(292,y1+1, 'R$^2$=%.2f' % (r_value ** 2,), rotation=2)

ax[1].scatter(doy, avgt)
ax[1].grid(True)
ax[1].set_xticks( (295, 305, 312, 319, 326, 335, 342, 349, 356) )
ax[1].set_xticklabels( ('Oct 22', 'Nov 1', 'Nov 8', 'Nov 15', 'Nov 22', 'Dec 1', 'Dec 8', 'Dec 15', 'Dec 22') )
ax[1].set_ylabel("Average Temp $^{\circ}\mathrm{F}$")
ax[1].set_xlim(290,360)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')