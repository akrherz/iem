# Generate some comparison data between ASOS sites, tricky, me thinks

import iemdb
import datetime
import numpy
import mx.DateTime
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()
acursor2 = ASOS.cursor()

# Get this year's hourly data
percentiles = numpy.zeros( (24,) )
d2011 = numpy.zeros( (24,) )
climate = numpy.zeros( (24,) )
acursor.execute("""
  SELECT extract(hour from valid + '10 minutes'::interval) as hr, avg(tmpf)
  from t2011 where valid BETWEEN '2011-07-01' and '2011-08-01' and 
  (extract(minute from valid) between 50 and 59 or 
        extract(minute from valid) = 0) and
  station = 'DSM' GROUP by hr ORDER by hr ASC
  """)
for row in acursor:
    hr = row[0]
    ob = row[1]
    # Lookup value
  
    acursor2.execute("""SELECT extract(year from valid) as yr,
     avg(tmpf), count(*) from alldata where station = 'DSM'
     and (extract(minute from valid) between 50 and 59 or 
        extract(minute from valid) = 0)
     and extract(hour from valid + '10 minutes'::interval) = %s
     and extract(month from valid) = 7 and valid < '2011-01-01'
     GROUP by yr ORDER by avg ASC
    """, (hr,))
    years = acursor2.rowcount + 1 # 2011
    place = 0
    for row in acursor2:
        if ob < row[1]:
           break
        place += 1
        
    print hr, ob, place, years
    percentiles[hr] = float(place) / float(years) * 100.
    d2011[hr] = ob

    acursor2.execute("""SELECT 
     avg(tmpf) from alldata where station = 'DSM'
     and (extract(minute from valid) between 50 and 59 or 
        extract(minute from valid) = 0)
     and extract(hour from valid + '10 minutes'::interval) = %s
     and extract(month from valid) = 7 and valid < '2011-01-01'
    """, (hr,))
    row = acursor2.fetchone()
    climate[hr] = row[0]

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(211)

ax.set_title("Des Moines July 2011 Hourly Temperatures (1932-2011)")

ax.bar(numpy.arange(0,24)-0.4, d2011-climate, fc='r')

ax.set_xlim(-0.5,23.5)
ax.set_xticks((0,4,8,12,16,20))
ax.set_xticklabels( ('Mid', '4 AM', '8 AM', 'Noon', '4 PM', '8 PM'))
ax.set_xlabel("All times CDT")
ax.set_ylabel("2011 Departure $^{\circ}\mathrm{F}$")
ax.grid(True)

ax = fig.add_subplot(212)
ax.bar(numpy.arange(0,24)-0.4, percentiles, fc='r')

ax.set_xlim(-0.5,23.5)
ax.set_xticks((0,4,8,12,16,20))
ax.set_xticklabels( ('Mid', '4 AM', '8 AM', 'Noon', '4 PM', '8 PM'))
ax.set_xlabel("All times CDT")
ax.set_ylabel("Percentile [100 warmest]")
ax.set_ylim(80,100)
ax.grid(True)


import iemplot
fig.savefig('test.ps')
iemplot.makefeature('test')
