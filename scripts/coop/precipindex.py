import psycopg2
DBCONN = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = DBCONN.cursor()

years = []
ratio = []
cursor.execute("""
select one.year, one.sum / two.sum, one.sum, two.sum from (select year, sum(precip) from alldata_ia where station = 'IA0000' and month in (4,5) GROUP by year) as one, (select year, sum(precip) from alldata_ia where station = 'IA0000' and month in (7,8) GROUP by year) as two WHERE one.year = two.year ORDER by one.year ASC
""")
atot = 0
btot = 0
for row in cursor:
    years.append( row[0] )
    ratio.append( row[1] )
    atot += row[2]
    btot += row[3]
    
import matplotlib.pyplot as plt
import numpy as np

ratio = np.array(ratio)
avgval = btot / atot
years = np.array(years)

(fig, ax) = plt.subplots(1,1)
bars = ax.bar(years-0.4, ratio, fc='b', ec='b')
for bar in bars:
    if bar.get_height() > 2 and bar.get_x() < 2012:
        ax.text(bar.get_x(), bar.get_height()+0.1, "%.0f" % (bar.get_x()+0.4,))
    if bar.get_height() > avgval:
        bar.set_facecolor('r')
        bar.set_edgecolor('r')
ax.plot([1892,2013], [avgval, avgval], color='k')
ax.set_xlim(1892.5,2013.5)
ax.set_ylabel("Ratio, average=%.2f" % (avgval,))
ax.set_xlabel("*2013 data thru 29 August")
ax.set_title("Iowa Ratio of Apr+May Precipitation to July+August")
ax.grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')