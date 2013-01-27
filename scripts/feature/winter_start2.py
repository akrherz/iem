import mx.DateTime
import numpy
import iemdb, iemplot
COOP = iemdb.connect("coop", bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""SELECT a.day, a.snow, a.low, c.low, a.high, c.high from 
 alldata_ia a JOIN climate c on (c.station = a.station and
 a.sday = to_char(c.valid, 'mmdd')) where
 a.station = 'IA2203' and a.day > '1900-01-01' ORDER by day ASC""")

clock = -1
hits = numpy.zeros((7), 'f')
count = numpy.zeros((7), 'f')
hhits = numpy.zeros((7), 'f')

for row in ccursor:
    if row[1] >= 1:
        clock = 0
    
    if clock > 6:
        clock = -1
        
    if clock > -1:
        count[clock] += 1
        if row[2] < row[3]:
            hits[clock] += 1
        if row[4] < row[5]:
            hhits[clock] += 1
        clock += 1
        
print hits
print count

from matplotlib import pyplot as plt

(fig, ax) = plt.subplots(1,1)

ax.bar(numpy.arange(7)-0.4, hits / count * 100.0, fc='b', width=0.4, label='Daily Low')
ax.bar(numpy.arange(7), hhits / count * 100.0, fc='r', width=0.4, label='Daily High')

ax.set_xticks( range(7))
ax.set_xticklabels(['Snow\nDate', 1, 2, 3, 4, 5, 6])
ax.set_ylabel("Frequency [%]")
ax.set_ylim(0, 100)
ax.set_yticks([0,25,50,75,100])
ax.set_title("Des Moines 1900-2012 Frequency of Temperature below Average\nAfter date of 1+ inch of snowfall")
ax.grid(True)
ax.set_xlabel("Days after Snowfall")
ax.legend()

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')