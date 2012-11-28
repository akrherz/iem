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
obs2 = obs.copy()
ytd1931 = numpy.zeros((366,), 'f')

for day in range(366):
    ytd1931[day] = numpy.average(obs1931[:(day+1)])


freq = numpy.zeros((366), 'f')
for dy in range(60,333):
    # Now, we replace each year's 1 Jan - 18 Jul with 2012
    obs2[:,0:dy] = obs[-1,0:dy]

    ytd = numpy.zeros((2013-1880, 366), 'f')

    for day in range(366):
        ytd[:,day] = numpy.average(obs2[:,:(day+1)],1)
    
    count = 0
    total = 2012-1880
    for year in range(1880,2012):
        if ytd[year-1880,-2] > ytd1931[-2]:
            count += 1
    freq[dy] = float(count) / float(total) * 100.0

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(2,1, sharex=True)

for year in range(1880,2013):
    if year == 2012:
        ax[0].plot(range(333), ytd[year-1880,:333], c='red', label='2012')
    else:
        ax[0].plot(range(366), ytd[year-1880,:], c='tan')

ax[0].plot(range(366), ytd1931[:], c='b', label='1931')
ax[0].set_ylabel("YTD Average Temperature $^{\circ}\mathrm{F}$")
ax[0].set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax[0].set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax[0].grid(True)
ax[0].set_title("Chance of 2012 being Warmest Year on Record for Des Moines\nScenarios: append previous year time series to this year's YTD value\n%s/%s (%.1f%%) years (1880-2011) finish warmer than 1931" % (count, total,
                                                                    float(count) / float(total) * 100.0))
ax[0].set_xlim(60,364)
ax[0].set_ylim(20,65)
ax[0].legend(loc=4)

ax[1].plot(range(333), freq[:333], c='r', label='1931')
ax[1].grid(True)
ax[1].set_ylabel("Scenario Probability [%]")
ax[1].set_ylim(0,100)

plt.tight_layout()
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
