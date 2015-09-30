import psycopg2

COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()

cursor.execute("""
 WITH climo as (
  SELECT to_char(valid, 'mmdd') as sday, high from climate51 where
  station = 'IA0200'),
 obs as (
  SELECT day, high, sday from alldata_ia where station = 'IA0200'
  and year > 2010)

 SELECT obs.high - climo.high, day from obs JOIN climo on (obs.sday = climo.sday)
 ORDER by day ASC
""")

data = []
for year in range(2011,2015):
  data.append([0,])

for row in cursor:
  doy = int(row[1].strftime("%j"))
  c = 1 if row[0] > 0 else 0
  data[row[1].year-2011].append( data[row[1].year-2011][-1] + c )

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

for i in range(len(data)):
    ax.plot(range(len(data[i])), data[i], lw=2,label='%s' % (2011+i,))

ax.legend(loc=4)
ax.plot([0,366],[0,366], '-.')
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.grid(True)
ax.set_xlim(0,367)
ax.set_ylim(0,367)
ax.set_ylabel("Accumulated Days Above Average")
ax.set_title("Ames Accumulated Days with High Temp Above Average")


fig.savefig('test.png')
