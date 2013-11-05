import psycopg2
import numpy as np

def do():
    conn = psycopg2.connect(database='asos', host='iemdb', user='nobody')
    cursor = conn.cursor()
    
    counts = np.zeros( (24,12), 'f')
    hits = np.zeros( (24,12), 'f')
    
    cursor.execute("""
    SELECT substring(tm,5,2) as mo, substring(tm,9,2) as hr,
    count(*), sum(case when lead > 0 then 1 else 0 end) from
    (SELECT tm, max, lead(max) OVER (ORDER by tm ASC),
    lag(max) OVER (ORDER by tm ASC) from
     (SELECT to_char(valid, 'YYYYMMDDHH24') as tm, max(coalesce(p01i,0)) from alldata
     WHERE station in ('DSM','DVN','OTM','ALO','MCW','MIW','SUX','CID',
     'IOW') and valid > '1972-01-01' GROUP by tm) as foo
     ) as foo2
     WHERE max > 0 GROUP by mo, hr
    """)
    
    for row in cursor:
        hr = int(row[1])
        mo = int(row[0]) - 1
        hits[hr,mo] = row[3]
        counts[hr,mo] = row[2]
 
    return hits, counts

hits, counts = do()

import matplotlib.pyplot as plt
import matplotlib.cm as cm
(fig, ax) = plt.subplots(1,1)

cmap = cm.get_cmap('jet_r')
res = ax.imshow( hits / counts *100.0, cmap=cmap, aspect='auto', interpolation='nearest')
ax.set_ylim(-0.5,23.5)
for hr in range(24):
    for mo in range(12):
        ax.text(mo, hr, "%.0f" % (hits[hr,mo] / counts[hr,mo] * 100.0,), 
                ha='center', va='center')
ax.set_yticks( (0,3,6,9,12,15,18,21) )
ax.set_yticklabels( ('Mid', '3 AM', '6 AM', '9 AM', 'Noon', '3 PM', '6 PM', '9 PM') )
ax.set_xticks( range(12))
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlabel("1972-2013 Iowa Sites with Hourly Precipitation")
ax.set_title("Frequency (%) of an hour with measurable precip\nfollowed by another hour with measurable precip")

fig.colorbar(res)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')