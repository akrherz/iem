import iemdb
import numpy
import mx.DateTime
COOP = iemdb.connect('coop', bypass=True)

ccursor = COOP.cursor()
ccursor2 = COOP.cursor()

# Get white christmases
ccursor.execute("""SELECT year from alldata_ia where sday = '1225' and
  snowd >= 1 and station = 'IA2203'""")

counts = numpy.zeros( (60,), 'f')

for row in ccursor:
    ccursor2.execute("""SELECT day, snowd from alldata_ia where
    station = 'IA2203' and sday < '1225' and year = %s ORDER by day DESC 
    LIMIT 60""", (row[0],))
    count = -2
    counts[-1] += 1
    for row2 in ccursor2:
        if row2[1] >= 1:
            counts[count] += 1
            count -= 1
        else:
            break
    #print row[0], count
    
ets = mx.DateTime.DateTime(2000, 12, 25)
sts = ets - mx.DateTime.RelativeDateTime(days=60)
xticks = []
xticklabels = []
for i in range(2,60,3):
    ts = sts + mx.DateTime.RelativeDateTime(days=i+1)
    xticks.append( i )

    xticklabels.append( ts.strftime("%-d\n%b"))

import matplotlib.pyplot as plt



(fig, ax) = plt.subplots(1, 1)

ax.bar(numpy.arange(60)-0.5, counts / counts[-1] * 100.0)
ax.set_xticks( xticks )
ax.set_xticklabels( xticklabels )
ax.set_xlim(23,60)
ax.set_ylim(0, 100)
ax.set_yticks( [0,25,50,75,100])
ax.grid(True)
ax.set_ylabel("Frequency [%]")
ax.set_title("When does White Christmas Come?\n Des Moines 1895-2011")
ax.text(26, 80, "53 years had White Christmas, by what\ndate did this snow cover appear by?",
        ha='left')

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')