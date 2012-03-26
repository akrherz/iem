# Produce a chart of 

import iemdb
import numpy
import mx.DateTime
ISUAG = iemdb.connect('isuag', bypass=True)
icursor = ISUAG.cursor()

import matplotlib.pyplot as plt
import numpy
fig = plt.figure()
ax = fig.add_subplot(111)

for yr in range(1988,2013):
  x = []
  y = []
  icursor.execute("""
 select valid, c30
 from daily WHERE station = 'A130209' 
 and valid >= '%s-01-01' and valid < '%s-05-01' ORDER by valid ASC
  """ % (yr,yr) )
  for row in icursor:
    x.append( int(row[0].strftime("%j")) )
    y.append( row[1] )

  if yr in [1988,1997]:
    continue

  color = 'skyblue'
  if yr == 2012:
    color = 'r'
  ax.plot(x, y, color=color)

ax.set_title("ISU AgClimate Ames Site 4 inch Soil Temperature\n1 Jan - 30 Apr Yearly Timeseries [1988-2012]")
ax.set_xlabel("Red Line is 1 Jan - 18 Mar 2012")
ax.grid(True)
ax.set_ylabel('Daily Avg Temp $^{\circ}\mathrm{F}$')
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlim(0,121)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
