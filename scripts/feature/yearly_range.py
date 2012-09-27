import iemdb, network
import numpy
import numpy.ma
import mx.DateTime

COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

#select extract(year from o.day + '2 months'::interval) as yr, sum(case when o.high > c.high then 1 else 0 end), count(*) from alldata_ia o , climate51 c WHERE c.station = o.station and o.station = 'IA0200' and extract(month from c.valid) = extract(month from o.day) and extract(day from c.valid) = extract(day from o.day) and (o.month in (11,12,1) or (o.month = 2 and extract(day from o.day) < 9)) and o.day > '1893-06-01' GROUP by yr ORDER by yr ASC
ccursor.execute("""
 select year, max(case when high > 89 then day else '1880-01-01'::date end), 
 avg((high+low)/2.0) from alldata_ia 
 where station = 'IA2203' and year < 2012 and year > 1879  GROUP by year ORDER by year ASC
""")

years = []
last = []
total = []
for row in ccursor:
    ts = mx.DateTime.strptime("%s%s%s" % (row[1].year, row[1].month, row[1].day), "%Y%m%d")
    years.append( row[0] )
    last.append( int(ts.strftime("%j")) )
    total.append( float(row[2]) )

years = numpy.array( years )
last = numpy.array( last )

import matplotlib.pyplot as plt
import iemplot

fig, ax = plt.subplots(2, 1)

bars = ax[0].bar(years-0.5, last, fc='pink', ec='pink')
for bar in bars:
    if bar.get_height() < numpy.average(last):
        bar.set_edgecolor('skyblue')
        bar.set_facecolor('skyblue')
ax[0].set_yticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax[0].set_yticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax[0].set_ylim(150,300)
ax[0].set_ylabel("Date of last 90+$^{\circ}\mathrm{F}$")
ax[0].set_title("1880-2011 Des Moines Last Date Above 90$^{\circ}\mathrm{F}$")
ax[0].set_xlim(1879.5,2012)
ax[0].grid(True)
ax[0].plot([1880,2011], [numpy.average(last), numpy.average(last)], color='k')

ax[1].scatter(total, last)
#ax[1].set_ylim(30,80)
ax[1].set_yticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax[1].set_yticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax[1].set_ylim(150,300)
ax[1].set_xlabel("Average Temperature for Year $^{\circ}\mathrm{F}$")
ax[1].set_ylabel("Date of last 90+$^{\circ}\mathrm{F}$")
ax[1].grid(True)


fig.savefig('test.ps')
iemplot.makefeature('test')
