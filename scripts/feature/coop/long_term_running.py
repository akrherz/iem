import numpy
import psycopg2
import datetime
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
ccursor = COOP.cursor()

station = 'IA0000'
# Get climatology
ccursor.execute("""
 SELECT sday, avg(precip) from alldata_ia where station = %s
 GROUP by sday
""", (station,))
climate = {}
for row in ccursor:
    climate[row[0]] = float(row[1])

running = [0,]
d30 = [0,]*30
running30 = []
d90 = [0,]*90
running90 = []
d365 = [0,]*365
running365 = []
dates = []

ccursor.execute("""
 SELECT day, precip, sday from alldata_ia where station = %s
 and day > '1900-01-01' ORDER by day ASC
""", (station,))
for row in ccursor:
    d = float(row[1]) - climate[ row[2] ]
    running.append( running[-1] + d )
    d30.pop()
    d30.insert(0, d )
    running30.append( sum(d30) )
    d90.pop()
    d90.insert(0, d )
    running90.append( sum(d90) )
    d365.pop()
    d365.insert(0, d )
    running365.append( sum(d365) )
    dates.append( row[0] )

import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=10)

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
(fig, ax) = plt.subplots(1,1)

#ax.plot(numpy.arange(0, len(running)), running)
ax.set_title("Iowa Precipitation Departure over Trailing Windows\n1 Jan 2014 - 12 Apr 2015")
#ax[0].set_ylabel("Departure [inch]")
#ax[0].plot(dates, running30, color='b', label='30 day')
#ax[0].plot(dates, running90, color='r', label='90 day')
#ax[0].plot(dates, running365, color='k', label='365 day')
#ax[0].set_xlim( datetime.date(1987,1,1), datetime.date(1989,10,4))
#ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
#ax[0].grid(True)
#ax[0].legend(ncol=3, prop=prop)

ax.set_ylabel("Departure [inch]")
ax.plot(dates, running30, color='b', label='30 day')
ax.plot(dates, running90, color='r', label='90 day')
ax.plot(dates, running365, color='k', label='365 day')
ax.set_xlim(datetime.date(2014,1,1), datetime.date(2015,4,12))
ax.set_ylim(-14, 14)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
ax.grid(True)
ax.legend(ncol=3, prop=prop)


#plt.xticks(rotation=90)
#plt.subplots_adjust(bottom=.15)
fig.savefig('test.png')
