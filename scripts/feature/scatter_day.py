import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
select foo2.year, foo.d, foo2.d, foo2.d - foo.d from 
 (select year, min(day) as d 
 from alldata where stationid = 'ia1063' and month > 8 and low < 32 
 GROUP by year) as foo, 
 (select year, min(day) as d from alldata where stationid = 'ia0200'
  and month > 8 and low < 32 and year > 1900 GROUP by year) as foo2 

WHERE foo2.year = foo.year ORDER by foo2.year ASC
""")

x = []
y = []
for row in ccursor:
    x.append( int(row[1].strftime("%j")) )
    y.append( int(row[2].strftime("%j")) )
    
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)

ax.scatter(x,y)

fig.savefig('test.png')