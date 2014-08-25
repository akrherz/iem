import numpy
import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

STATION = 'IA0000'

# Which years where above
above = []
below = []
ccursor.execute("""SELECT extract(year from day + '3 months'::interval) as yr, 
  sum(precip) from alldata_ia where
  station = %s and day >= '1893-10-01' and day < '2011-10-01' 
  GROUP by yr ORDER by sum DESC""",
  (STATION,))
years = ccursor.rowcount

for row in ccursor:
    if len(above) > (years/2):
        below.append( row[0] )
    else:
        above.append( row[0] )
    
# Get monthly averages
monthly_climate = [0]*12
ccursor.execute("""SELECT month, avg(sum) from 
    (SELECT year, month, sum(precip) from alldata_ia
    WHERE station = %s and year < 2012 GROUP by year, month) as foo
    GROUP by month""", (STATION,))
for row in ccursor:
    monthly_climate[ row[0] - 1 ] = row[1]
    
# Loop over years
hits = numpy.zeros((12,), 'f')
for year in above:
    ccursor.execute("""
    SELECT month, sum(precip) from alldata_ia where station = '%s'
    and day BETWEEN '%.0f-10-01' and '%.0f-10-01' GROUP by month
    """ %  (STATION, year-1, year))
    for row in ccursor:
        if row[1] > monthly_climate[row[0]-1]:
            hits[row[0]-1] += 1.0
bhits = numpy.zeros((12,), 'f')
for year in below:
    ccursor.execute("""
    SELECT month, sum(precip) from alldata_ia where station = '%s'
    and day BETWEEN '%.0f-10-01' and '%.0f-10-01' GROUP by month
    """ % (STATION, year-1, year))
    for row in ccursor:
        if row[1] < monthly_climate[row[0]-1]:
            bhits[row[0]-1] += 1.0
            
print hits

import matplotlib
import matplotlib.pyplot as plt

fig, ax = plt.subplots(1,1)

bars = ax.bar( numpy.arange(1,13) - 0.4, hits / float(len(above)) * 100.0, width=0.4,
        facecolor='skyblue', label='Year Above - Month Above')
bars[4].set_facecolor('b')
bars = ax.bar( numpy.arange(1,13), bhits / float(len(above)) * 100.0, width=0.4,
        facecolor='pink', label='Year Below - Month Below')
bars[4].set_facecolor('r')
ax.set_title("Frequency of Monthly Precipitation Departure in the\nSame Direction as the Water Year (Oct-Sep) Departure (Iowa 1894-2011)")
ax.set_xticks( numpy.arange(1,13) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlim(0,13)
ax.set_ylabel("Percentage of Years [%]")
ax.legend(loc=1)
ax.set_yticks( numpy.arange(0,101,25))
ax.set_ylim(0,100)
ax.grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')