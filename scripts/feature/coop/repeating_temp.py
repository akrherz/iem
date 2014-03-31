import psycopg2
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()

cursor.execute("""
 SELECT doy, count(*), sum(case when lead >= 70 then 1 else 0 end) from 
 (SELECT extract(doy from day) as doy, high, lead(high) OVER (ORDER by day ASC)
 from alldata_ia where station = 'IA2203') as foo
 WHERE high >= 70 GROUP by doy ORDER by doy ASC""")

doy = []
freq = []

for row in cursor:
    doy.append( row[0] )
    freq.append( row[2] / float(row[1]) * 100.)


import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

ax.bar(doy, freq, ec='r', fc='r')
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlim(1,367)
ax.set_ylabel("Frequency [%]")
ax.grid(True)
ax.set_title("1886-2014 Des Moines Frequency of One 70+$^\circ$F High\nfollowed by another day with a 70+$^\circ$F high")
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')