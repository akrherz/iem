import iemdb, network
import numpy
import numpy.ma
import mx.DateTime

COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

#select extract(year from o.day + '2 months'::interval) as yr, sum(case when o.high > c.high then 1 else 0 end), count(*) from alldata_ia o , climate51 c WHERE c.station = o.station and o.station = 'IA0200' and extract(month from c.valid) = extract(month from o.day) and extract(day from c.valid) = extract(day from o.day) and (o.month in (11,12,1) or (o.month = 2 and extract(day from o.day) < 9)) and o.day > '1893-06-01' GROUP by yr ORDER by yr ASC
ccursor.execute("""
 select year, min(low) from alldata_ia 
 where sday < '1008' and month > 7 GROUP by year ORDER by year ASC
 """)

years = []
mins = []
for row in ccursor:
    years.append( row[0] )
    mins.append( float(row[1]) )

mins[-1] = 13

years = numpy.array( years )
mins = numpy.array( mins )

ccursor.execute("""
 select year, min(case when low < 14 then sday else '1231' end) from
 alldata_ia WHERE month > 7 GROUP by year ORDER by year ASC
 """)
jdays = []
for row in ccursor:
    ts = mx.DateTime.strptime("2000"+row[1], '%Y%m%d')
    jdays.append( int(ts.strftime("%j")) )

jdays[-1] = 281

import matplotlib.pyplot as plt
import iemplot

fig, ax = plt.subplots(2, 1, sharex=True)

bars = ax[0].bar(years-0.5, mins, fc='pink', ec='pink')
for bar in bars:
    if bar.get_height() <= bars[-1].get_height():
        bar.set_edgecolor('skyblue')
        bar.set_facecolor('skyblue')
#ax[0].set_yticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
#ax[0].set_yticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
#ax[0].set_ylim(150,300)
ax[0].set_ylabel("Lowest Temperature $^{\circ}\mathrm{F}$")
ax[0].set_title("1893-2012 Iowa Lowest Temperature prior to 8 October\nIsolated 12$^{\circ}\mathrm{F}$ reported on 7 Oct 2012, previous earliest 6 Oct 1935")
ax[0].set_xlim(1892.5,2012.6)
ax[0].grid(True)
#ax[0].plot([1880,2011], [numpy.average(last), numpy.average(last)], color='k')

bars = ax[1].bar(years, jdays, fc='b', ec='b')
for bar in bars:
    if bar.get_height() <= bars[-1].get_height():
        bar.set_edgecolor('r')
        bar.set_facecolor('r')
#ax[1].set_ylim(30,80)
ax[1].set_yticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax[1].set_yticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax[1].set_ylim(min(jdays)-10, max(jdays)+5)
#ax[1].set_xlabel("Average Temperature for Year $^{\circ}\mathrm{F}$")
ax[1].set_ylabel("Date of first sub 13$^{\circ}\mathrm{F}$")
ax[1].grid(True)


fig.savefig('test.ps')
iemplot.makefeature('test')
