import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

# Query all obs
ccursor.execute("""SELECT day, precip from alldata 
        where stationid = 'ia2203' ORDER by day ASC""")

running = 0
yearmax = [0]*(2011-1893)
streak7 = [0]*(2011-1893)
for row in ccursor:
    if row[1] > 0.001:
        if running > yearmax[row[0].year-1893]:
            yearmax[row[0].year-1893] = running
        running = 0
    running += 1
    if running == 7:
        streak7[row[0].year-1893] += 1
    
import matplotlib.pyplot as plt
import numpy

fig = plt.figure()
ax = fig.add_subplot(211)

ax.bar(numpy.arange(1893,2011), yearmax, facecolor='tan', edgecolor='tan')
ax.set_title("Des Moines: Maximum Daily Dry Streak")
ax.set_ylabel('Number of Days')
ax.grid(True)
ax.set_xlim(1893,2011)

ax = fig.add_subplot(212)
ax.bar(numpy.arange(1893,2011), streak7, facecolor='tan', edgecolor='tan')
ax.set_title('Des Moines: Number of 7+ Day Dry Periods')
ax.set_ylabel('Number of Events')
ax.set_xlabel('* 2010 data thru 13 Oct')
ax.grid(True)
ax.set_xlim(1893,2011)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')