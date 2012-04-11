import iemdb, network
import numpy

COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

#select extract(year from o.day + '2 months'::interval) as yr, sum(case when o.high > c.high then 1 else 0 end), count(*) from alldata_ia o , climate51 c WHERE c.station = o.station and o.station = 'IA0200' and extract(month from c.valid) = extract(month from o.day) and extract(day from c.valid) = extract(day from o.day) and (o.month in (11,12,1) or (o.month = 2 and extract(day from o.day) < 9)) and o.day > '1893-06-01' GROUP by yr ORDER by yr ASC
ccursor.execute("""
 select year, max(case when low < 29 then extract(doy from day) else 0 end), max(case when low < 32 then extract(doy from day) else 0 end) from alldata_ia where station = 'IA0200' and montH < 6 GROUP by year ORDER by year ASC
""")

years = []
b29 = []
b32 = []

for row in ccursor:
    years.append( row[0] )
    b29.append( float(row[1])  )
    b32.append( float(row[2])  )


years = numpy.array( years )
b29 = numpy.array( b29 )
b32 = numpy.array( b32 )
print b32-b29
import matplotlib.pyplot as plt
import iemplot

fig = plt.figure()
ax = fig.add_subplot(211)

ag = numpy.average(b29)
bars = ax.bar( years - 0.4, b29, fc='b', ec='b')
for bar in bars:
  if bar.get_height() < ag:
    bar.set_facecolor('r')
    bar.set_edgecolor('r')

ax.set_yticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_yticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlim(1892.5, 2013.5)
ax.set_title("Ames Date of Last Low Temperature Below... [1893-2012]")
ax.set_ylim(60,152)
ax.grid(True)
bars[-1].set_edgecolor('g')
bars[-1].set_facecolor('g')

ax.set_ylabel('Date below 29 $^{\circ}\mathrm{F}$')

ax2 = fig.add_subplot(212)

ag = numpy.average(b32)
ax2.set_yticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax2.set_yticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
bars = ax2.bar( years - 0.4, b32, fc='b', ec='b')
for bar in bars:
  if bar.get_height() < ag:
    bar.set_facecolor('r')
    bar.set_edgecolor('r')
bars[-1].set_edgecolor('g')
bars[-1].set_facecolor('g')
ax2.set_xlim(1892.5, 2013.5)
ax2.set_ylim(60,152)
ax2.grid(True)
ax2.set_ylabel('Date below 32 $^{\circ}\mathrm{F}$')
ax2.set_xlabel("*2012 thru 26 March")


fig.savefig('test.ps')
iemplot.makefeature('test')
