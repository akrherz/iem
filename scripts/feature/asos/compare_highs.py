import psycopg2
IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
cursor = IEM.cursor()

panc = []
dsm = []
cursor.execute("""
 WITH panc as (
 SELECT day, max_tmpf from summary_2014 s JOIN stations t on (t.iemid = s.iemid)
 WHERE t.id = 'PANC' and t.network = 'AK_ASOS' ORDER by day ASC),
 dsm as (
 SELECT day, max_tmpf from summary_2014 s JOIN stations t on (t.iemid = s.iemid)
 WHERE t.id = 'ALO' and t.network = 'IA_ASOS' ORDER by day ASC)
 SELECT p.day, p.max_tmpf, d.max_tmpf from panc p JOIN dsm d on (d.day = p.day)
 WHERE d.day < '2014-05-19' ORDER by p.day ASC
""")
dates = []
for row in cursor:
    dates.append(row[0])
    panc.append(row[1])
    dsm.append(row[2])
    
IEM = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = IEM.cursor()
    
climo = []
cursor.execute("""
 WITH panc as (
 SELECT valid as day, high from ncdc_climate71 where station = 'AK0280' and
 valid < '2000-05-19' ORDER by valid ASC),
 dsm as (
 SELECT valid as day, high from ncdc_climate71 where station = 'IA8706' and
 valid < '2000-05-19' ORDER by valid ASC)
 SELECT p.day, p.high, d.high from panc p JOIN dsm d on (d.day = p.day)
 WHERE p.day != '2000-02-29' ORDER by p.day ASC
""")
for row in cursor:
    climo.append(row[2] - row[1])
    
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates

dsm = np.array(dsm)
panc = np.array(panc)

(fig, ax) = plt.subplots(1,1)
diff = dsm - panc
print len(dates), len(climo)
bars = ax.bar( dates, diff, ec='b', fc='b')
ax.plot( dates, climo, color='k', label='Climatology Difference')
above = 0
for i, bar in enumerate(bars):
    if diff[i] > 0:
        bar.set_facecolor('r')
        bar.set_edgecolor('r')
        above += 1
below = len(dates) - above
ax.grid(True)
#ax.set_xlim(0.5,29.5)
ax.set_ylabel("High Temperature Difference $^\circ$F")
ax.set_title("2014 Daily High Temperature Difference\nWaterloo, Iowa minus Anchorage, Alaska")
ax.text(dates[32], 35, "Waterloo Warmer (%s days)" % (above,), color='r', ha='center')
ax.text(dates[88], -45, "Anchorage Warmer (%s days)" % (below,), color='b', ha='center')
ax.xaxis.set_major_formatter(mdates.DateFormatter('%-d %b'))


fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
