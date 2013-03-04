import iemdb
import numpy
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

data = []
days = []

counts = numpy.zeros( (10,), 'f')
allhits = numpy.zeros( (10,), 'f')
greaterhits = numpy.zeros( (10,), 'f')

ccursor.execute("""SELECT day, case when snow > 8 then 8 else snow end 
 from alldata_ia where
 station = 'IA2203' and day > '1893-01-01' ORDER by day ASC""")

for row in ccursor:
    snow = row[1]
    if row[1] < 0.1:
        snow = 0.
    data.append( snow )
    days.append( row[0] )
    
def getidx(val):
    if val == 0:
        return 0
    if val < 1:
        return 1
    return int(val) + 1
    
# 0,1,2,3,4,5,6,7
#     x x x x
for i in range(len(data)-5):
    if days[i].month not in (11,12,1,2,3):
        continue
    idx = getidx(data[i])
    counts[ idx ] += 1.0
    if max( data[i+2:i+6] ) > data[i]:
        greaterhits[ idx ] += 1.0
    if max( data[i+2:i+6] ) > 0:
        allhits[ idx ] += 1.0
    
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

ax.bar(numpy.arange(-1,9)-0.4, allhits / counts * 100.,
       label='Any Snow Event')
ax.bar(numpy.arange(-1,9)-0.2, greaterhits / counts * 100., width=0.4, fc='r', zorder=2,
       label='Event Greater')
ax.set_xticks( numpy.arange(-1,9))
ax.set_xticklabels(("No\nSnow", '< 1"', "1", "2", "3", "4", "5", "6", "7", "8+"))
ax.set_xlim(-1.5,8.5)
ax.set_title("1893-2012 Des Moines Day 2 thru 5 Snowfall Frequency")
ax.set_xlabel("Daily Snowfall Event (1 November thru 1 April)")
ax.set_ylabel("Frequency [%]")
ax.legend()
ax.grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')