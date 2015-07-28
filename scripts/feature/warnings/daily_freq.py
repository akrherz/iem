import matplotlib.pyplot as plt
import psycopg2

dbconn = psycopg2.connect(database='postgis', user='nobody', host='iemdb')
cursor = dbconn.cursor()

cursor.execute("""
 SELECT d, count(*), sum(c) from
 (SELECT extract(doy from issue) as d, extract(year from issue) as yr, 
 count(*) as c from sbw
 where status = 'NEW' and significance = 'W' and phenomena in ('SV','TO')
 and issue > '2002-01-01' and issue < '2015-01-01'
 GROUP by d, yr) as foo
 GROUP by d ORDER by d ASC

""")

days = []
cnt = []
avg = []
for row in cursor:
    days.append( row[0] )
    cnt.append( float(row[1]) / 13.0 * 100.0)
    avg.append( float(row[2]) / 13.0 )

(fig, ax) = plt.subplots(1,1)
ax.bar(days, cnt, fc='green', ec='green')

y2 = ax.twinx()
y2.bar(days, avg, fc='skyblue', ec='skyblue')
ax.grid(True)
#y2.grid(ls="-", lw=5, zorder=-1) 
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlim(0,366)
ax.set_title("2002-2012 United States Daily\nSevere T'Storm + Tornado Warning Frequencies")
ax.set_ylabel("Percent Years with 1+ Warning [%]", color='green')
y2.set_ylabel("Average Warning Count", color='skyblue')

y2.tick_params(axis='y', colors='skyblue')
ax.tick_params(axis='y', colors='green')

fig.savefig('test.png')
