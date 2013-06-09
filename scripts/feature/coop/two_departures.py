import iemdb
import numpy
COOP = iemdb.connect('coop', bypass=True)
cursor = COOP.cursor()

cursor.execute("select first.year, first.sum, second.sum from (select year, sum(gdd50(high,low)) from alldata_ia where station = 'IA0200' and month in (5,6) and sday < '0609' GROUP by year ORDER by sum ASC) as first, (select year, sum(gdd50(high,low)) from alldata_ia where station = 'IA0200' and month in (5,6,7,8,9) GROUP by year ORDER by sum ASC) as second WHERE first.year = second.year ORDER by first.year ASC")

first = numpy.zeros( (cursor.rowcount,))
second = numpy.zeros( (cursor.rowcount,))

for i, row in enumerate(cursor):
    first[i] = row[1]
    second[i] = row[2]

first_avg = numpy.average(first)
second_avg = numpy.average(second[:-1])

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

# first departure was -100 and result was 100, then we'd want 100 - 100
delta = (second[:-1] - second_avg) - (first[:-1] - first_avg)
bars = ax.bar( first[:-1] - first_avg, delta, 
       bottom=(first[:-1] - first_avg), width=5, ec='None', fc='r')
for i, bar in enumerate(bars):
    if delta[i] < 0:
        bar.set_facecolor('b')

ax.grid(True)
ax.plot([first[-1] - first_avg, first[-1] - first_avg], [-500,500], color='k',
   lw=2., linestyle='--')
ax.text(first[-1] - first_avg, -475, ' 2013', ha='left')
ax.text(20,-430, 'Bars represent change from\n1 May - 9 Jun departure to\nfinal 1 May - 1 Oct departure', bbox=dict(facecolor='r', alpha=0.2) )
ax.set_ylim(-500,500)

ax.set_ylabel("1 May - 1 Oct GDD Departure")
ax.set_xlabel("1 May - 9 Jun GDD Departure")
ax.set_title("1893-2013 Ames Growing Degree Days (base=50,ceil=86)")

fig.savefig('test.svg')
import iemplot
iemplot.makefeature('test')
