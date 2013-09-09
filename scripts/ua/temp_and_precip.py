'''
 Compute the difference between the 12 UTC 850 hPa temp and afternoon high
'''
from pyiem.datatypes import temperature
import psycopg2
import datetime
ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
acursor = ASOS.cursor()

POSTGIS = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
pcursor = POSTGIS.cursor()

tmpf = []
precip = []
pcursor.execute("""
 select valid, tmpc from raob_profile p JOIN raob_flights f on 
 (p.fid = f.fid) where f.station in ('KOAX', 'KOVN', 'KOMA')  and 
 p.pressure = 700 and extract(hour from valid at time zone 'UTC') = 00
 and extract(month from valid) = 8
 and tmpc > -40
 ORDER by valid ASC
""")
for row in pcursor:
    valid = row[0]
    t850 = temperature(row[1], 'C')
    acursor.execute("""select sum(max) from (SELECT extract(hour from valid) as hr, max(p01i) from t"""+ str(valid.year) +"""
    WHERE station = 'OMA' and valid BETWEEN %s and %s GROUP by hr) as foo
    """, (valid, valid + datetime.timedelta(hours=12)))
    row2 = acursor.fetchone()
    if row2[0] is None:
        continue
    tmpf.append( t850.value("F") )
    precip.append( row2[0] )
    
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

ax.scatter(tmpf, precip)
ax.set_title("1960-2013 Omaha Daytime High Temp vs 12 UTC 850 hPa Temp")
ax.set_ylabel(r"Temperature Difference $^\circ$C")
ax.grid(axis='y')

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
