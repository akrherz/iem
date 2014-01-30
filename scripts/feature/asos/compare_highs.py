import psycopg2
IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
cursor = IEM.cursor()

panc = []
dsm = []
cursor.execute("""
 WITH panc as (
 SELECT day, max_tmpf from summary_2014 s JOIN stations t on (t.iemid = s.iemid)
 WHERE t.id = 'PAOM' and t.network = 'AK_ASOS' ORDER by day ASC),
 dsm as (
 SELECT day, max_tmpf from summary_2014 s JOIN stations t on (t.iemid = s.iemid)
 WHERE t.id = 'ALO' and t.network = 'IA_ASOS' ORDER by day ASC)
 SELECT p.day, p.max_tmpf, d.max_tmpf from panc p JOIN dsm d on (d.day = p.day)
 ORDER by p.day ASC
""")
for row in cursor:
    panc.append(row[1])
    dsm.append(row[2])
    
IEM = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = IEM.cursor()
    
c_panc = []
c_dsm = []
cursor.execute("""
 WITH panc as (
 SELECT valid as day, high from ncdc_climate71 where station = 'AK6496' and
 valid < '2000-02-01' ORDER by valid ASC),
 dsm as (
 SELECT valid as day, high from ncdc_climate71 where station = 'IA8706' and
 valid < '2000-02-01' ORDER by valid ASC)
 SELECT p.day, p.high, d.high from panc p JOIN dsm d on (d.day = p.day)
 ORDER by p.day ASC
""")
for row in cursor:
    c_panc.append(row[1])
    c_dsm.append(row[2])
    
import matplotlib.pyplot as plt
import numpy as np

dsm = np.array(dsm)
panc = np.array(panc)

(fig, ax) = plt.subplots(1,1)
diff = dsm - panc
bars = ax.bar( np.arange(1,31)-0.5, diff, ec='b', fc='b')
for i, bar in enumerate(bars):
    if diff[i] > 0:
        bar.set_facecolor('r')
        bar.set_edgecolor('r')
ax.grid(True)
ax.set_xlim(0.5,30.5)
ax.set_ylabel("High Temperature Difference $^\circ$F")
ax.set_title("High Temperature Difference\nWaterloo, Iowa minus Nome, Alaska")
ax.text(22, 25, "Waterloo Warmer", color='r', ha='center')
ax.text(12, -45, "Nome Warmer", color='b', ha='center')


fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')