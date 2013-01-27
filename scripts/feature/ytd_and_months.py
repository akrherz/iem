import iemdb
import matplotlib.pyplot as plt
import numpy
(fig, ax) = plt.subplots(2,1)

COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

def get_daily(year):
    data = []
    ccursor.execute("""SELECT day, (high+low)/2.0 from alldata_ia
    WHERE station = 'IA0000' and year = %s ORDER by day ASC""", (year,))
    for row in ccursor:
        data.append( float(row[1]) )
    return numpy.array( data )

def get_monthly(year):
    data = []
    ccursor.execute("""SELECT month, avg((high+low)/2.0) from alldata_ia
        WHERE station = 'IA0000' and year = %s GROUP by month
        ORDER by month ASC""", (year,))
    for row in ccursor:
        data.append( float(row[1]) )
    return numpy.array( data )

monavg = numpy.array([ 20.15,
 24.24,
 36.27,
 49.75,
 60.84,
 70.22,
 74.83,
 72.59,
 64.36,
 52.69,
 37.73,
 24.95])

daily2012 = get_daily(2012)
daily1931 = get_daily(1931)
mon2012 = get_monthly(2012)
mon1931 = get_monthly(1931)

ytd2012 = []
ytd1931 = []

for i in range(1,len(daily1931)+1):
    ytd1931.append( numpy.average(daily1931[:i]))
    
for i in range(1,len(daily2012)+1):
    ytd2012.append( numpy.average(daily2012[:i]))
    
#ax[0].plot(numpy.arange(1,367), ytd2012, color='k', linewidth=4)
#ax[0].plot(numpy.arange(1,366), ytd1931, color='k', linewidth=4)
ax[0].plot(numpy.arange(1,366), ytd1931, color='orange', label='1931 - 53.4$^{\circ}\mathrm{F}$', linewidth=2)
ax[0].plot(numpy.arange(1,367), ytd2012, color='green', label='2012 - 53.3$^{\circ}\mathrm{F}$', linewidth=2)
ax[0].set_ylabel("YTD Temp Departure $^{\circ}\mathrm{F}$")
ax[0].grid(True)
ax[0].set_xlim(1,367)
ax[0].legend(loc=4)
ax[0].set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax[0].set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax[0].set_title("Iowa Year to Date and Monthly Average Temperature")

ax[1].bar(numpy.arange(1,13)-0.3, mon1931 - monavg, width=0.3, color='orange', label='1931')
ax[1].bar(numpy.arange(1,13), mon2012 - monavg, width=0.3, color='green', label='2012')
ax[1].set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug',
                        'Sep','Oct','Nov','Dec') )
ax[1].set_xticks( numpy.arange(1,13))
ax[1].set_xlim(0.5,12.5)
ax[1].legend(loc=(0.5,0.8), ncol=2)
ax[1].set_ylabel("Avg Temp Departure $^{\circ}\mathrm{F}$")
ax[1].grid(True)
ax[1].set_xlabel("*** IEM Estimates, NCDC has 1931: 52.1$^{\circ}\mathrm{F}$ and 2012: 51.8$^{\circ}\mathrm{F}$")


fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')