# high 35.98
# low 17.3
# select extract(year from issue) as yr, count(*) from warnings WHERE
# phenomena in ('SV','TO') and gtype = 'C' and significance = 'W' and
#extract(month from issue) = 4 GROUP by yr ORDER by yr ASC
#select y, count(*) from (select distinct extract(year from valid) as y, to_char(valid, 'YYYYMMDDHH24') as h from alldata WHERE station = 'DSM' and drct >= 180 and drct < 270 and extract(doy from valid) BETWEEN extract(doy from '2000-04-01'::date) and extract(doy from '2000-05-19'::date) and sknt >= 5 and valid > '1973-01-01') as foo GROUP by y ORDER by y
import iemdb
POSTGIS = iemdb.connect('postgis', bypass=True)
pcursor = POSTGIS.cursor()
pcursor2 = POSTGIS.cursor()

years = []
tvals = []
svals = []
jday = []
pcursor.execute("""
 select extract(year from issue) as yr, sum(case when phenomena = 'TO' then 1 else 0 end),
  sum(case when phenomena = 'SV' then 1 else 0 end) from warnings WHERE
 phenomena in ('SV','TO') and gtype = 'P' and significance = 'W' and
 extract(doy from issue) < 26 GROUP by yr ORDER by yr ASC
""")
for row in pcursor:
    years.append( float(row[0]) )
    tvals.append( float(row[1]) )
    svals.append( float(row[2]) )

#vals[-1] = 99

import numpy
import matplotlib.pyplot as plt

svals = numpy.array( svals )
tvals = numpy.array( tvals )
years = numpy.array( years )

fig = plt.figure()
ax = fig.add_subplot(111)
rects = ax.bar( years - 0.4, tvals + svals , fc='b', ec='b', label='Severe Tstorm')

#rects[-1].set_facecolor('r')
for rect in rects:
  y = rect.get_height()
  x = rect.get_x()
  ax.text(x+0.3,y+15,"%.0f"%(y,), weight='bold', 
          ha='center', color='k')
rects = ax.bar( years - 0.4, tvals  , fc='r', ec='r', label='Tornado')
#  if y > averageVal:
#      rect.set_facecolor("r")
 #     rect.set_edgecolor('r')
ax.set_xlim(2001.5, 2012.5)
#ax.plot([1893,2011],[averageVal,averageVal], color='black')
#ax.set_ylim(80,160)
#ax.set_yticks((91,121,152))
#ax.set_yticklabels(('Apr 1', 'May 1', 'Jun 1'))

ax.set_ylabel("Warnings Count")
#ax.set_xlabel("*2011 thru 16 August")
ax.grid(True)
ax.legend(loc=2)
#ax.set_ylim(55,70)
ax.set_title("1-25 January Severe T'Storm + Tornado Warnings (CONUS)")

fig.savefig('test.ps')

import iemplot
iemplot.makefeature('test')
    
