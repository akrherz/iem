import iemdb, network
import numpy

COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
    select yr, max(s), min(s) from 
    (select stationid, extract(year from (day + '1 month'::interval)) as yr
    , sum(precip) as s 
    from alldata where stationid in 
      (select distinct stationid from alldata 
      where year = 1950 and precip > 0 and 
      stationid not in ('ia7842') ) 
      and month in (12,1,2) and day >= '1951-12-01' 
      GROUP by stationid, yr) as foo 
    GROUP by yr ORDER by yr ASC
""")

maxv = []
minv = []

for row in ccursor:
    maxv.append( row[1] )
    minv.append( row[2] )

ccursor.execute("""
 SELECT  extract(year from (day + '1 month'::interval)) as yr, sum(precip) from alldata WHERE
 stationid = 'ia0200' and month in (12,1,2) and day > '1951-12-01'
 GROUP by yr ORDER by yr ASC
""")
ames = []
for row in ccursor:
    ames.append( row[1] )

ccursor.execute("""
 SELECT  extract(year from (day + '1 month'::interval)) as yr, sum(precip) from alldata WHERE
 stationid = 'ia0000' and month in (12,1,2) and day > '1951-12-01'
 GROUP by yr ORDER by yr ASC""")
iowa = []
for row in ccursor:
    iowa.append( row[1] )

maxv = numpy.array( maxv )
minv = numpy.array( minv )
import matplotlib.pyplot as plt
import iemplot

fig = plt.figure()
ax = fig.add_subplot(111)

ax.bar( numpy.arange(1951, 2010) - 0.4, maxv-minv, bottom=minv,
        facecolor='#EEEEEE', zorder=1)
ax.scatter( numpy.arange(1951,2010), ames, color='r', zorder=2,
            label='Ames')
ax.scatter( numpy.arange(1951,2010), iowa, color='b', zorder=2,
            label='Iowa Avg')
ax.set_xlim(1950.5, 2009.5)
ax.set_title("Iowa Dec/Jan/Feb Precipitation Range\nas reported from 37 long term climate sites")
ax.grid(True)
ax.legend(loc=2)
ax.set_xlabel('Year of December included')
ax.set_ylabel('Precipitation [inch]')
fig.savefig('test.ps')
iemplot.makefeature('test')