# Produce a chart of 

import iemdb
import mx.DateTime
ISUAG = iemdb.connect('isuag', bypass=True)
icursor = ISUAG.cursor()

icursor.execute("""
select extract(year from valid) as year, 
min( case when c30 < 50 then valid else '2012-01-01'::date end), 
max( case when c30 >= 50 then valid else '1950-01-01'::date end) 
from daily WHERE station = 'A130209' and extract(month from valid) > 7 
GROUP by year ORDER by year ASC
""")
sdoy = []
edoy = []
years = []
for row in icursor:
    sdoy.append( int(row[1].strftime("%j")) )
    edoy.append( int(row[2].strftime("%j")) )
    years.append( row[0] )

import matplotlib.pyplot as plt
import numpy
fig = plt.figure()
ax = fig.add_subplot(111)
sdoy = numpy.array( sdoy )
years = numpy.array( years )

ax.bar(years - 0.5, sdoy)
yticks = []
yticklabels = []
for mo in (10,):
  for dy in (1, 8, 15, 22, 29):
    ts = mx.DateTime.DateTime(2000,mo,dy)
    yticks.append( int(ts.strftime("%j")) )
    yticklabels.append( ts.strftime("%b %d") )
ax.set_yticks( yticks )
ax.set_yticklabels( yticklabels )
ax.set_ylim(270,310)
ax.set_xlim(1985.5,2010.5)
ax.set_title("ISU AgClimate Ames Site 4 inch Soil Temperature\nFirst Day of the Fall Season below 50$^{\circ}\mathrm{F}$")
ax.grid(True)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
