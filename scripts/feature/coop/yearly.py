import psycopg2

COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()

cursor.execute("""SELECT year, sum(narr_srad), sum(hrrr_srad),
 avg(high) from alldata_ia
  WHERE station = 'IA0200' and year > 1978 and month = 9 GROUP by year """)

years = []
rad = []
t = []

for row in cursor:
    years.append( row[0] )
    rad.append( max(row[1], row[2]) )
    t.append( row[3] )
    
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1, 1)
ax.bar(years, rad)
ax.set_ylim(450,700)

y2 = ax.twinx()
y2.scatter(years, t)

fig.savefig('test.png')