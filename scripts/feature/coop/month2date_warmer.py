import psycopg2

IEM = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = IEM.cursor()

ratio = []
for i in range(1,31):
    cursor.execute("""
    SELECT sum(case when sep.avg >= jul.avg then 1 else 0 end), count(*) from
    (SELECT year, avg((high+low)/2.0) from alldata_ia WHERE
    station = 'IA2203' and month = 7 and sday <= '07%02i' GROUP by year) as jul,
    (SELECT year, avg((high+low)/2.0) from alldata_ia WHERE
    station = 'IA2203' and month = 9 and sday <= '09%02i' GROUP by year) as sep
    WHERE sep.year = jul.year
    """ % (i,i))
    row = cursor.fetchone()
    ratio.append( row[0] / float(row[1]) * 100.0 )
    
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)
import numpy as np
bars = ax.bar( np.arange(1,31) -0.4, ratio)
ax.set_ylabel("Frequency [%]")
ax.set_title("1880-2012 Des Moines Frequency of September\nwarmer than July for first number of days of each month")
ax.grid(True)
ax.set_xlim(0.5,31)
ax.set_xlabel("Each Month to day")

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')