import psycopg2
import numpy
import datetime
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()

# 50 to 120
in_summer = numpy.zeros( (70,))
counts = numpy.zeros( (70,))
in_jja = numpy.zeros( (70,))
cofreq = numpy.zeros( (70,))

for year in range(1893,2013):
    cursor.execute("""
    SELECT extract(doy from day) as doy, high, month from alldata_ia where
    station = 'IA2203' and year = %s ORDER by doy
    """, (year,))
    data = numpy.zeros( (366,), 'f')
    for row in cursor:
        data[ int(row[0])-1] = row[1]
        if row[2] in [6,7,8]:
            in_jja[ int(row[1]) - 50 ] += 1.0
        
    # Find hottest period
    running = 0
    idx0 = None
    for i in range(0,366-91):
        total = numpy.sum( data[i:i+91] )
        if total > running:
            running = total
            idx0 = i
    idx1 = idx0 + 91
    
    for i, high in enumerate(data):
        if high < 50:
            continue
        counts[ high - 50 ] += 1.0
        if i >= idx0 and i < idx1:
            in_summer[ high - 50 ] += 1.0
            ts = datetime.datetime(year, 1, 1) + datetime.timedelta(days=i)
            if ts.month in [6,7,8]:
                cofreq[ high - 50 ] += 1.0

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

ax.bar(numpy.arange(50,120)-0.4, in_summer / counts  * 100., fc='r', ec='r',
       label='in 91 warmest days')
ax.plot(numpy.arange(50,120), in_jja / counts * 100.0, lw=3, zorder=2, c='k',
        label='During Jun/Jul/Aug')
ax.plot(numpy.arange(50,120), cofreq / counts * 100.0, lw=3, zorder=2, c='b',
        label='Both')
ax.legend(loc='best')
ax.set_xlim(49.5, 111)
ax.set_yticks(numpy.arange(0,101,10))
ax.grid(True)
ax.set_ylabel("Percentage of High Temperature Events")
ax.set_xlabel("Daily High Temperature $^{\circ}\mathrm{F}$")
ax.set_title("1893-2012 Des Moines Daily High Temperature\nFrequency of High Temp within period of 91 warmest days")

fig.savefig('test.png')