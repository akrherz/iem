# high 35.98
# low 17.3
# select extract(year from issue) as yr, count(*) from warnings WHERE
# phenomena in ('SV','TO') and gtype = 'C' and significance = 'W' and
#extract(month from issue) = 4 GROUP by yr ORDER by yr ASC
import iemdb
POSTGIS = iemdb.connect('asos', bypass=True)
pcursor = POSTGIS.cursor()

years = []
vals = []
pcursor.execute("""
select y, count(*) from (select distinct extract(year from valid) as y, to_char(valid, 'YYYYMMDDHH24') as h from alldata WHERE station = 'DSM' and drct >= 180 and drct < 270 and extract(doy from valid) BETWEEN extract(doy from '2000-04-01'::date) and extract(doy from '2000-05-19'::date) and sknt >= 5 and valid > '1973-01-01') as foo GROUP by y ORDER by y
""")
for row in pcursor:
    years.append( float(row[0]) )
    vals.append( float(row[1]) )

import numpy
import matplotlib.pyplot as plt

vals = numpy.array( vals )
years = numpy.array( years )

fig = plt.figure()
ax = fig.add_subplot(111)
rects = ax.bar( years - 0.4, vals )
#for rect, label in zip(rects, labels):
#  y = rect.get_height()
#  x = rect.get_x()
#  ax.text(x+0.3,y-5,label.strftime("%b %-d"), weight='bold', rotation=90, color='white')
ax.set_xlim(1972.5, 2011.5)
#ax.set_ylim(80,160)
#ax.set_yticks((91,121,152))
#ax.set_yticklabels(('Apr 1', 'May 1', 'Jun 1'))

ax.set_ylabel("Hours with 1+ Observation")
ax.set_xlabel("*2011 Total of 106 hours is the least")
ax.grid(True)
#ax.set_ylim(35,75)
ax.set_title("Des Moines: Hours with at least one ob of\nsouthwesterly (S,SSW,SW,WSW) winds >= 5 knots [1 April - 19 May]")

fig.savefig('test.ps')

import iemplot
iemplot.makefeature('test')
    
