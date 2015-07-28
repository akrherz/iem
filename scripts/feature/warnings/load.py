import psycopg2

pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
cursor = pgconn.cursor()

def getp(phenomena):
    cursor.execute("""
     WITH data as 
     (SELECT t, count(*) from
     (select phenomena, generate_series(issue, expire, '1 minute'::interval) as t
     from sbw_2014 where status = 'NEW' and issue > '2014-04-27' and
     phenomena in %s) as foo
     GROUP by t),
     
     ts as (select generate_series('2014-04-27 00:00-05'::timestamptz,
      '2014-04-29 05:30-05'::timestamptz, '1 minute'::interval) as t) 
      
     SELECT ts.t, data.count from ts LEFT JOIN data on (data.t = ts.t)
     ORDER by ts.t ASC
    """, (phenomena,))
    times = []
    counts = []
    for row in cursor:
        times.append( row[0] )
        counts.append( row[1] if row[1] is not None else 0 )
        
    return times, counts

to_t, to_c = getp( ('TO',))
b_t, b_c = getp( ('SV', 'TO') )

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates
import pytz

def fill_between(x, y1, y2=0, ax=None, **kwargs):
    """Plot filled region between `y1` and `y2`.

    This function works exactly the same as matplotlib's fill_between, except
    that it also plots a proxy artist (specifically, a rectangle of 0 size)
    so that it can be added it appears on a legend.
    """
    ax = ax if ax is not None else plt.gca()
    ax.fill_between(x, y1, y2, **kwargs)
    p = plt.Rectangle((0, 0), 0, 0, **kwargs)
    ax.add_patch(p)
    return p

(fig, ax) = plt.subplots(1,1)

fill_between(b_t, np.zeros(len(b_t)), b_c, zorder=1, color='teal',
                label="SVR T'Storm + Tornado")
fill_between(to_t, np.zeros(len(to_c)), to_c, zorder=2,
                color='red', label='Tornado')
ax.grid(True)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%I %p\n%d %b',
                                                      tz=pytz.timezone("America/Chicago")))

ax.set_title("27-29 April 2014 National Weather Service Warning Load")
ax.set_ylabel("Active Warning Count")
ax.legend(loc=2)
ax.set_xlabel("Central Daylight Time, thru 5:30 AM 29 April 2014")

fig.savefig('test.png')
