import mx.DateTime
import numpy
from scipy import stats
import iemdb, iemplot
COOP = iemdb.connect("coop", bypass=True)
ccursor = COOP.cursor()

def getc(v):
    if v > 23.35:
        return 'r'
    if v > 21.3956:
        return 'y'
    if v > 18.82:
        return 'g'
    return 'b'

vals = []
colors = []
mins = []
for yr in range(1900,2010):
    data = numpy.zeros( (366,) )
    ccursor.execute("""
    SELECT day, (high + low)/2.0 from alldata where stationid = 'ia0200' and 
    day >= '%s-06-01' and day < '%s-06-01' ORDER by day ASC
    """ % (yr, yr+1))
    
    i= 0
    for row in ccursor:
        data[i] = row[1]
        i += 1

    minv = 100.
    pos = 0

    for i in range(0,275):
        val = numpy.average(data[i:i+91])
        if val < minv:
            minv = val
            pos = i+90
    mins.append( minv )
    vals.append( pos + 1)
    colors.append( getc(minv) )

h_slope, intercept, h_r_value, p_value, std_err = stats.linregress(numpy.arange(0,110), vals)
vals = numpy.array(vals)


labels = []
xticks = []
sts = mx.DateTime.DateTime(2000,6,1)
for i in range(150,330,1):
    ts = sts + mx.DateTime.RelativeDateTime(days=(i-1))
    if ts.day in [1,]:
        labels.append( ts.strftime("%b %d") )
        xticks.append( i )

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)
v91 = vals - 91
vals[:] = 90
bars = ax.barh(numpy.arange(1900,2010) - 0.3, vals, left=(v91), facecolor='b', edgecolor='b')
i = 0
for bar in bars:
    bar.set_facecolor( getc(mins[i]) )
    bar.set_edgecolor( getc(mins[i]) )
    i += 1
ax.plot([intercept,intercept+(110.0*h_slope)],[1900,2010], c='#000000')
ax.set_xticklabels( labels )
ax.set_xticks( xticks )
ax.set_ylim(1899.5,2025.5)

p1 = plt.Rectangle((0, 0), 1, 1, fc="r")
p2 = plt.Rectangle((0, 0), 1, 1, fc="y")
p3 = plt.Rectangle((0, 0), 1, 1, fc="g")
p4 = plt.Rectangle((0, 0), 1, 1, fc="b")
ax.legend([p1,p2,p3,p4], ["Warmest 25%","","","Coldest 25%"], ncol=4)
leg = plt.gca().get_legend()
ltext  = leg.get_texts()
plt.setp(ltext, fontsize='small')
ax.set_title("Ames [1900-2010] Coldest 91 day period")

ax.grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')