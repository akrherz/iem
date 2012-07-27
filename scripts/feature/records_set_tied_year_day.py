import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

records = {}

ccursor.execute("""
  SELECT sday, high, year, extract(doy from day) 
  from alldata_ia where station = 'IA2203'
  ORDER by day ASC""")

years = []
doy = []
set_years = []
set_doy = []

for row in ccursor:
    if not records.has_key(row[0]):
      records[row[0]] = -9999
    if row[1] >= records[row[0]]:
      if row[1] > records[row[0]]:
        set_years.append( row[2] )
        set_doy.append( row[3] )
      else:
        years.append( row[2] )
        doy.append( row[3] )
      records[row[0]] = row[1]

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

fig, ax = plt.subplots(1,1)
ax.scatter(doy, years, marker='+', c='g', edgecolor='g', zorder=2, label='Tied')
ax.scatter(set_doy, set_years, marker='+', c='r', edgecolor='r', zorder=3, label='Set')
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.grid(True)
ax.set_xlim(0,366)
ax.set_ylim(1875,2014.5)
rect = plt.Rectangle((182,1958), 30, 2013-1858, fc='#eeeeee', zorder=1)
ax.add_patch(rect)
ax.set_ylabel("Year")
ax.set_xlabel("thru 8 July 2012")
ax.set_title("Des Moines Dates of Record High Temperatures [1878-2012]")
ax.legend(ncol=2,loc=(0.,-0.12))
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
