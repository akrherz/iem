import psycopg2
import numpy
from scipy import stats
import psycopg2.extras
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)
"""
data = {}
for line in open('/home/akrherz/Downloads/corn_yield.csv'):
    tokens = line.split(",")
    if tokens[0] != '"SURVEY"':
        continue
    year = tokens[1].replace('"', '')
    data[int(year)] = float(tokens[-1].replace('"', ''))

years = range(1893,2012)
yields = []
for year in years:
    yields.append( data[year] )

h_slope, intercept, r_value, p_value, std_err = stats.linregress(years, yields)
departures = []
for year in years:
    expected = h_slope * year + intercept
    departures.append( (data[year] - expected ) / expected * 100.0)
departures.append( 0 )
"""
# Get current sigmas
ccursor.execute("""
 SELECT stddev(sp) as p, avg(sp) as pavg, 
        stddev(tp) as t, avg(tp) as tavg  from 
 (SELECT year, sum(precip) as sp, sum(gdd50(high::numeric,low::numeric)) as tp
  from alldata_ia
  where station = 'IA0000' and month = 7
  GROUP by year) as foo
""")
row = ccursor.fetchone()
pstd = float(row['p'])
pavg = float(row['pavg'])
tstd = float(row['t'])
tavg = float(row['tavg'])

ccursor.execute("""SELECT year, sum(precip) as sp, 
  sum(gdd50(high::numeric,low::numeric)) as tp from alldata_ia
  where station = 'IA0000' and month = 7
  GROUP by year ORDER by year ASC""")

tsigma = []
psigma = []
years = []
dist = []
for row in ccursor:
    t = float((float(row['tp']) - tavg) / tstd)
    p = float((float(row['sp']) - pavg) / pstd)
    d = ((t * t) + (p * p))**0.5
    tsigma.append( t )
    psigma.append( p )
    dist.append( d )
    years.append( row['year'] )
    print '%s,%.4f,%.4f,%.2f,%.2f' % (row['year'], t, p, row['tp'], row['sp'])

tsigma = numpy.array( tsigma )
psigma = numpy.array( psigma )
print tsigma[-2], psigma[-2]
import matplotlib.pyplot as plt
from matplotlib.patches import Circle


h_slope, intercept, r_value, p_value, std_err = stats.linregress(tsigma, psigma)
print r_value ** 2
y1 = -4.0 * h_slope + intercept
y2 = 4.0 * h_slope + intercept
(fig, ax) = plt.subplots(1,1)

ax.scatter(tsigma, psigma)
ax.plot([-4,4], [y1,y2])
ax.text(-3.8,y1+0.1, 'R$^2$=%.2f' % (r_value ** 2,), rotation=-10)
ax.set_xlim(-4,4)
ax.set_ylim(-5,5)
for i in range(len(years)):
    #if years[i] in [1988,2011]:
    #    ax.text( tsigma[i], psigma[i], ' %.0f' % (years[i],), va='top')
    if years[i] in [2014,] or dist[i] > (dist[-1]):
        ax.text( tsigma[i], psigma[i], ' %.0f' % (years[i],), va='center')

c = Circle((0,0), radius=dist[-1], facecolor='none')
ax.add_patch(c)
ax.set_xlabel("Growing Degree Day Departure ($\sigma$)")
ax.set_ylabel("Precipitation Departure ($\sigma$)")
ax.grid(True)
ax.set_title("July Iowa Statewide Temp + Precip Departure\nbased on IEM estimated areal averaged data (1893-2014)")

import iemplot
fig.savefig('test.ps')
iemplot.makefeature('test')
