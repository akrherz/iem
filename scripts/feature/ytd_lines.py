import numpy
import iemdb
COOP = iemdb.connect("coop", bypass=True)
ccursor = COOP.cursor()

obs = numpy.zeros((2013-1880, 366), 'f')

ccursor.execute("""
 SELECT year, extract(doy from day), (high+low)/2.0 from alldata_ia
 where station = 'IA2203' and day >= '1880-01-01'
""")
for row in ccursor:
    obs[int(row[0])-1880,int(row[1])-1] = row[2]

# Save 1931 (record year)
obs1931 = obs[1931-1880,:].copy()

# Now, we replace each year's 1 Jan - 18 Jul with 2012
obs[:,0:200] = obs[-1,0:200]

ytd = numpy.zeros((2013-1880, 366), 'f')
ytd1931 = numpy.zeros((366,), 'f')

for day in range(366):
    ytd[:,day] = numpy.average(obs[:,:(day+1)],1)
    ytd1931[day] = numpy.average(obs1931[:(day+1)])

count = 0
total = 2012-1880
for year in range(1880,2012):
    if ytd[year-1880,-2] > ytd1931[-2]:
        count += 1

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

for year in range(1880,2012):
    ax.plot(range(366), ytd[year-1880,:], c='tan')

ax.plot(range(366), ytd1931[:], c='r', label='1931')
ax.set_ylabel("YTD Average Temperature $^{\circ}\mathrm{F}$")
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.grid(True)
ax.set_title("Chance of 2012 being Warmest Year on Record for Des Moines\nScenarios: append previous year time series to this year's YTD value\n%s/%s (%.1f%%) years (1880-2011) finish warmer than 1931" % (count, total,
                                                                    float(count) / float(total) * 100.0))
ax.set_xlim(200,364)
ax.set_ylim(50,65)
ax.legend()
plt.tight_layout()
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')