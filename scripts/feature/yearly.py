# high 35.98
# low 17.3
# select extract(year from issue) as yr, count(*) from warnings WHERE
# phenomena in ('SV','TO') and gtype = 'C' and significance = 'W' and
#extract(month from issue) = 4 GROUP by yr ORDER by yr ASC
#select y, count(*) from (select distinct extract(year from valid) as y, to_char(valid, 'YYYYMMDDHH24') as h from alldata WHERE station = 'DSM' and drct >= 180 and drct < 270 and extract(doy from valid) BETWEEN extract(doy from '2000-04-01'::date) and extract(doy from '2000-05-19'::date) and sknt >= 5 and valid > '1973-01-01') as foo GROUP by y ORDER by y
import iemdb
POSTGIS = iemdb.connect('coop', bypass=True)
pcursor = POSTGIS.cursor()
pcursor2 = POSTGIS.cursor()

years = []
vals = []
jday = []
pcursor.execute("""
select year, max(precip) from alldata where stationid = 'ia0200' GROUP by year ORDER by year ASC
""")
for row in pcursor:
    years.append( float(row[0]) )
    vals.append( float(row[1]) )
    pcursor2.execute("""SELECT extract(doy from day) from alldata where
    stationid = 'ia0200' and year = %s and precip = %s
    """, (row[0], row[1]))
    row2 = pcursor2.fetchone()
    jday.append( row2[0] )

#vals[-1] = 99

import numpy
import matplotlib.pyplot as plt

vals = numpy.array( vals )
averageVal = numpy.average(vals)
years = numpy.array( years )

fig = plt.figure()
ax = fig.add_subplot(211)
rects = ax.bar( years - 0.4, vals , fc='b', ec='b')
#rects[-1].set_facecolor('r')
for rect in rects:
  y = rect.get_height()
#  x = rect.get_x()
#  ax.text(x+0.3,y-5,label.strftime("%b %-d"), weight='bold', rotation=90, color='white')
  if y > averageVal:
      rect.set_facecolor("r")
      rect.set_edgecolor('r')
ax.set_xlim(1892.5, 2011.5)
ax.plot([1893,2011],[averageVal,averageVal], color='black')
#ax.set_ylim(80,160)
#ax.set_yticks((91,121,152))
#ax.set_yticklabels(('Apr 1', 'May 1', 'Jun 1'))

ax.set_ylabel("Max Daily Precip [inch]")
ax.set_xlabel("*2011 thru 16 August")
ax.grid(True)
#ax.set_ylim(55,70)
ax.set_title("Ames 1893-2011 Daily Precipitation Maximum per year\nMax: %.2f (1954) Average: %.2f" % (numpy.max(vals), averageVal))

ax = fig.add_subplot(212)
ax.scatter( jday, vals)
ax.grid(True)
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_ylabel("Max Daily Precip [inch]")
ax.set_xlabel("Day of Year")
fig.savefig('test.ps')

import iemplot
iemplot.makefeature('test')
    
