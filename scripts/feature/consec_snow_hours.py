import iemdb
import numpy
import numpy.ma
import mx.DateTime
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

acursor.execute(""" 
 select distinct to_char(valid, 'YYYYmmddHH24') as d from alldata 
 where station = 'DSM' 
 and metar ~* 'SN' ORDER by d ASC
""")

running = 0
maxrunning = numpy.ma.zeros( (2013-1948), 'f')
lts = mx.DateTime.DateTime(2000,1,1)
for row in acursor:
    ts = mx.DateTime.strptime(row[0], '%Y%m%d%H')
    if (ts - lts).hours == 1:
        running += 1
    else:
        running = 1
    lts = ts
    if running > maxrunning[ts.year-1948]:
        maxrunning[ts.year-1948] = running
        print maxrunning[ts.year-1948], ts
        
maxrunning.mask = numpy.where(maxrunning < 6, True, False)
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

ax.bar( numpy.arange(1948,2013)-0.5, maxrunning, ec='purple', fc='purple')
ax.set_xlim(1947.5, 2012.5)

ax.set_title("Des Moines Airport Max Consecutive Hours of Snow")
ax.set_xlabel("1965-1972 data unavailable")
ax.set_ylabel("Consecutive Hours [days]")
ax.set_yticks( numpy.arange(24,24*4,24))
ax.set_yticklabels( [1,2,3])
ax.grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
