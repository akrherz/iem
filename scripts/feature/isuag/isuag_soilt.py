# Produce a chart of 

import psycopg2
import numpy
import mx.DateTime
ISUAG = psycopg2.connect(database='isuag', host='localhost', port=5555, user='mesonet')
icursor = ISUAG.cursor()
from pyiem.datatypes import temperature
import matplotlib.pyplot as plt
import numpy
fig = plt.figure()
ax = fig.add_subplot(111)

climo = []
cdays = []
icursor.execute("""SELECT extract(doy from valid) as d, avg(c30)
from daily where station = 'A130209' GROUP by d ORDER by d ASC""")
for row in icursor:
    climo.append( row[1] )
    cdays.append( row[0] )

for yr in range(1988,2016):
    x = []
    y = []
    if yr < 2014:
        units = 'F'
        icursor.execute("""
     select valid, c30
     from daily WHERE station = 'A130209' 
     and valid >= '%s-01-01' and valid < '%s-01-01' ORDER by valid ASC
      """ % (yr,yr+1) )
    else:
        units = 'C'
        icursor.execute("""SELECT valid, tsoil_c_avg from sm_daily WHERE
        station = 'AEEI4' and valid >='%s-01-01' and
        valid < '%s-01-01' ORDER by valid ASC""" % (yr, yr+1))
    for row in icursor:
        x.append( int(row[0].strftime("%j")) +1 )
        y.append( temperature(row[1], units).value('F') )
        
    if yr in [1988,1997]:
        continue

    color = 'skyblue'
    if yr == 2015:
        color = 'r'
        ax.plot(x, y, color=color, label='2015', lw=2)
    else:
        ax.plot(x, y, color=color)

ax.plot(cdays, climo, color='k', label='Average')

ax.set_title("ISU AgClimate Ames Site 4 inch Soil Temperature\nYearly Timeseries [1988-2015]")
ax.set_xlabel("* 2015 thru 25 November")
ax.grid(True)
ax.set_ylabel('Daily Avg Temp $^{\circ}\mathrm{F}$')
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlim(0,367)
ax.set_ylim(-10,90)
ax.axhline(32, lw=2, color='purple', zorder=4)
ax.set_yticks(range(-10,90,20))
ax.legend(loc='best')
fig.savefig('151126.png')
