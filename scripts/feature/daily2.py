import numpy

import iemdb
import mx.DateTime
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
select extract( doy from o.day) as doy, count(*), sum(case when o.high > c.high then 1 else 0 end), sum(case when o.low > c.low then 1 else 0 end) from alldata o, climate71 c where o.station = 'IA0200' and o.day >= '2001-01-01' and to_char(o.day, 'MMDD') = to_char(c.valid, 'MMDD') 
and c.station = 'IA0200' GROUP by doy ORDER by doy ASc
""")

highs = []
lows = []
for row in ccursor:
  highs.append( row[2] / float(row[1]) )
  lows.append( row[3] / float(row[1]) )

highs = numpy.array(highs)
lows = numpy.array(lows)

xticks = []
xticklabels = []
for i in range(0,len(highs)):
  ts = mx.DateTime.DateTime(2000,1,1) + mx.DateTime.RelativeDateTime(days=i)
  if ts.day == 1:
    xticks.append( i )
    xticklabels.append( ts.strftime("%-d\n%b") )
  elif (ts.day + 1) % 2 == 0:
    xticks.append( i )
    xticklabels.append( ts.strftime("%-d") )

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(211)
bars = ax.bar( numpy.arange(len(highs))-0.4, highs * 100., ec='#45EC4B', fc='#45EC4B')
for bar in bars:
  if bar.get_y() < 0:
    bar.set_facecolor('blue')
    bar.set_edgecolor('blue')
ax.grid(True)
ax.set_xticks( xticks )
ax.set_xticklabels( xticklabels)
#ax.set_xlim(0,len(highs)+2)
ax.set_xlim(273.5,305.5)
ax.set_ylim(0,100)
ax.set_title("Ames 2001-2011 Percentage of Days above 1971-2000 Average", color='blue')
ax.set_ylabel("High Temperature", color='blue') 

ax2 = fig.add_subplot(212)
bars = ax2.bar( numpy.arange(len(lows)) -0.4, lows * 100., ec='#BE69CB', fc='#BE69CB')
for bar in bars:
  if bar.get_y() < 0:
    bar.set_facecolor('green')
    bar.set_edgecolor('green')
ax2.grid(True)
ax2.set_xticks( xticks )
ax2.set_xticklabels( xticklabels)
#ax2.set_xlim(0,len(highs)+2)
ax2.set_ylim(0,100)
ax2.set_xlim(273.5,305.5)
ax2.set_ylabel("Low Temperature", color='blue') 

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
