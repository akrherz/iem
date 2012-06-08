import iemdb, network
import numpy
import numpy.ma

COOP = iemdb.connect('asos', bypass=True)
ccursor = COOP.cursor()

#select extract(year from o.day + '2 months'::interval) as yr, sum(case when o.high > c.high then 1 else 0 end), count(*) from alldata_ia o , climate51 c WHERE c.station = o.station and o.station = 'IA0200' and extract(month from c.valid) = extract(month from o.day) and extract(day from c.valid) = extract(day from o.day) and (o.month in (11,12,1) or (o.month = 2 and extract(day from o.day) < 9)) and o.day > '1893-06-01' GROUP by yr ORDER by yr ASC
ccursor.execute("""
select doy, year, count(*) from (select distinct extract(year from valid) as year, extract(hour from valid) as hour, extract(doy from valid) as doy from alldata where station = 'DSM'  and p01i > 0) as foo GROUP by doy, year
""")

doy = []
count = []
data = numpy.ma.zeros((24,366), 'f')

for row in ccursor:
    data[:int(row[2])-1,int(row[0])-1] += 1

data.mask = numpy.where(data==0,True,False)

import matplotlib.pyplot as plt
import iemplot

fig, ax = plt.subplots(1, 1)

#ax.scatter( doy, count)
res= ax.imshow(data,aspect='auto', interpolation='nearest', extent=[1,366,0.5,24.5],
          origin='lower')
fig.colorbar(res)

ax.set_yticks( numpy.arange(1,25,4))
ax.set_ylabel("Hours")

ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlim(0, 366)
ax.set_title("Des Moines Hours with Precipitation Reported [1933-2012]\nFrequency of Number of Hours per Day of Year")
ax.set_ylim(0.5,24.5)
ax.grid(True)


fig.savefig('test.ps')
iemplot.makefeature('test')
