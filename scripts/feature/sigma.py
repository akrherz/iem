import iemdb
import numpy
from scipy import stats
import psycopg2.extras
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)

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

# Get current sigmas
ccursor.execute("""
 SELECT stddev(sum) as p, avg(sum) as pavg, stddev(avg) as t, avg(avg) as tavg  from 
 (SELECT year, sum(precip), avg((high+low)/2.0) from alldata_ia
  where station = 'IA0000' and sday >= '0501' and sday < '0814'
  GROUP by year) as foo
""")
row = ccursor.fetchone()
pstd = row['p']
pavg = row['pavg']
tstd = row['t']
tavg = row['tavg']

ccursor.execute("""SELECT year, sum(precip), avg((high+low)/2.0) from alldata_ia
  where station = 'IA0000' and sday >= '0501' and sday < '0814'
  GROUP by year ORDER by year ASC""")

tsigma = []
psigma = []
years = []
dist = []
for row in ccursor:
    t = float((row['avg'] - tavg) / tstd)
    p = float((row['sum'] - pavg) / pstd)
    d = ((t * t) + (p * p))**0.5
    tsigma.append( t )
    psigma.append( p )
    dist.append( d )
    years.append( row['year'] )
    print '%s,%.4f,%.4f,%.2f,%.2f' % (row['year'], t, p, row['avg'], row['sum'])

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
ax.text(-3.8,y1+0.1, 'R$^2$=%.2f' % (r_value ** 2,), rotation=-20)
ax.set_xlim(-4,4)
ax.set_ylim(-4,4)
for i in range(len(years)):
    if years[i] in [1988,2011]:
        ax.text( tsigma[i], psigma[i], ' %.0f' % (years[i],), va='top')
    elif years[i] in [2012,] or dist[i] > (dist[-1] - .9):
        ax.text( tsigma[i], psigma[i], ' %.0f' % (years[i],), va='center')

c = Circle((0,0), radius=dist[-1], facecolor='none')
ax.add_patch(c)
ax.set_xlabel("Temperature Departure ($\sigma$)")
ax.set_ylabel("Precipitation Departure ($\sigma$)")
ax.grid(True)
ax.set_title("1 May - 14 Aug Iowa Statewide Temp + Precip Departure\nbased on IEM estimated areal averaged data (1893-2012)")

import iemplot
fig.savefig('test.ps')
iemplot.makefeature('test')
