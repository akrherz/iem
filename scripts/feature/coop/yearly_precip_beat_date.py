import psycopg2
import numpy

COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()

precip = numpy.zeros( (2014-1893, 366))

cursor.execute("""SELECT year, extract(doy from day), precip from alldata_ia
 WHERE station = 'IA8706' and precip > 0 and year > 1898""")
for row in cursor:
    precip[ row[0] - 1893, row[1] - 1] = row[2]
    

years = []
jdays = []
prev = 0
for yr in range(1893,2014):
    sums = numpy.cumsum(precip[yr-1893,:])
    idx = numpy.digitize([prev,], sums)
    if idx < 200:
        print "%s total: %s prev: %s idx: %s" % (yr, sums[-1], prev, idx)
        years.append( yr )
        jdays.append( idx )
    prev = sums[-1]

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

# 2013: 21.42  2012: 20.45
ax.scatter(years, jdays, s=40, marker='s')
ax.scatter([2013], [146], s=40, marker='s', facecolor='r')
ax.text(2013, 149, "26 May\n2013", va='bottom', ha='right')
ax.set_yticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_yticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_title("1900-2013 Mason City Precipitation\nDate when year to date precip exceeds entire previous year")
ax.set_ylabel("Date of Exceedance")

ax.grid(True)
ax.set_xlim(1900,2015)
ax.set_ylim(120,367)

fig.savefig('test.png')
