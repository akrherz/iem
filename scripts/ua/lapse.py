'''
'''
from pyiem.datatypes import temperature
import psycopg2
import datetime


POSTGIS = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
pcursor = POSTGIS.cursor()

data = [0]*12
for i in range(12):
    data[i] = []
pcursor.execute("""
SELECT p500.valid, p500.tmpc, p500.height, p850.tmpc, p850.height from
 (select valid, tmpc, height from raob_profile_2013 p JOIN raob_flights f on 
 (p.fid = f.fid) where f.station in ('KOAX', 'KOVN', 'KOMA')  and 
 p.pressure = 500 and extract(hour from valid at time zone 'UTC') = 0
 and tmpc > -80) as p500 JOIN
 (select valid, tmpc, height from raob_profile_2013 p JOIN raob_flights f on 
 (p.fid = f.fid) where f.station in ('KOAX', 'KOVN', 'KOMA')  and 
 p.pressure = 850 and extract(hour from valid at time zone 'UTC') = 0
 and tmpc > -80) as p850
 ON (p850.valid = p500.valid)
""")
for row in pcursor:
    valid = row[0]
    lapse = (row[3] - row[1]) / ((row[2] - row[4]) / 1000.0)
    data[valid.month-1].append( lapse )

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1, figsize=(10,7))

ax.text(6, 10.5, "UNSTABLE", color='red', alpha=0.2, fontsize=30, zorder=1, ha='center',
        va='center')
ax.plot([0.5,12.5], [6,6], '-', lw=1.5, color='green', zorder=2)
ax.text(6, 7.5, "CONDITIONAL", color='green', alpha=0.2, fontsize=30, zorder=1, ha='center',
        va='center')
ax.plot([0.5,12.5], [9.5,9.5], '-', lw=1.5, color='green', zorder=2)
ax.text(6, 4, "STABLE", color='blue', alpha=0.2, fontsize=30, zorder=1, ha='center',
        va='center')
ax.boxplot(data)
ax.set_title("1960-2013 Omaha Sounding 00 UTC Monthly Climatology\n850 to 500 hPa Lapse Rates")
ax.set_ylabel(r"Lapse Rate, $\Gamma=\frac{^\circ\mathrm{C}}{{\mathrm{km}}}$")
ax.set_xticks(range(1,13))
ax.set_ylim(0,11.5)
ax.set_xticklabels(("Jan", 'Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.grid(axis='y')

fig.savefig('test.png')
#import iemplot
#iemplot.makefeature('test')