# Generate some comparison data between ASOS sites, tricky, me thinks

import psycopg2
import numpy as np
ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
acursor = ASOS.cursor()
acursor2 = ASOS.cursor()

# Get this year's hourly data
percentiles = np.zeros( (24,) )
today = np.zeros( (24,) )
climate = np.zeros( (24,) )
acursor.execute("""
  SELECT extract(hour from valid + '10 minutes'::interval) as hr, avg(tmpf)
  from t2014 where valid BETWEEN '2014-05-14 23:50' and '2014-05-15 23:50' and 
  (extract(minute from valid) between 50 and 59 or 
        extract(minute from valid) = 0) and
  station = 'DSM' GROUP by hr ORDER by hr ASC
  """)
for row in acursor:
    hr = row[0]
    ob = row[1]
    # Lookup value
  
    acursor2.execute("""SELECT 
     sum(case when tmpf < %s then 1 else 0 end),
     sum(case when tmpf > %s then 1 else 0 end)
     from alldata where station = 'DSM'
     and (extract(minute from valid) between 50 and 59 or 
        extract(minute from valid) = 0)
     and extract(hour from valid + '10 minutes'::interval) = %s
     and extract(month from valid) = 5 and 
     extract(day from valid) between 11 and 19 and valid < '2014-01-01'
     
    """, (ob, ob, hr))
    row2 = acursor2.fetchone()
    place = row2[0] / float(row2[0] + row2[1]) * 100.
        
    print hr, ob, place
    percentiles[hr] = float(place) 
    today[hr] = ob

    acursor2.execute("""SELECT 
     avg(tmpf) from alldata where station = 'DSM'
     and (extract(minute from valid) between 50 and 59 or 
        extract(minute from valid) = 0)
     and extract(hour from valid + '10 minutes'::interval) = %s
     and extract(month from valid) = 5 and
     extract(day from valid) between 11 and 19 and valid < '2014-01-01'
    """, (hr,))
    row = acursor2.fetchone()
    climate[hr] = row[0]

import matplotlib.pyplot as plt

fig, ax = plt.subplots(2,1, sharex=True)

ax[0].set_title("Des Moines 15 May 2014 Hourly Temperatures\nversus 11-18 May 1932-2013 Hourly Climatology")

ax[0].plot(np.arange(0,24), today, label='2014')
ax[0].plot(np.arange(0,24), climate, label='Climatology')
ax[0].legend(loc=2)
ax[0].grid(True)
ax[0].set_ylabel("Temperature $^\circ$F")
ax[0].set_xlim(-0.5,23.5)

ax[1].bar(np.arange(0,24)-0.4, percentiles, fc='b', label='vs 11-18 May 1932-2013')

ax[1].grid(True)
ax[1].set_xticklabels( ('Mid', '4 AM', '8 AM', 'Noon', '4 PM', '8 PM', 'Mid'))
ax[1].set_xticks(np.arange(0,25,4))
ax[1].set_ylabel("Percentile Rank [0=coldest]")


import iemplot
fig.savefig('test.ps')
iemplot.makefeature('test')
