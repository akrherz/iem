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

rL = obs[2012-1880,:].copy()
ccursor.execute("""
 SELECT extract(doy from valid), (min_high+min_low)/2.0 from climate
 where station = 'IA2203' and valid >= '2000-12-05'
""")
for row in ccursor:
    rL[int(row[0])-1] = row[1]

# Save 1931 (record year)
obs1931 = obs[1931-1880,:].copy()
obs2 = obs.copy()
ytd1931 = numpy.zeros((366,), 'f')
ytdrL = numpy.zeros((366,), 'f')

for day in range(366):
    ytd1931[day] = numpy.average(obs1931[:(day+1)])
    ytdrL[day] = numpy.average(rL[:(day+1)])


freq = numpy.zeros((366), 'f')
for dy in range(60,340):
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

(fig, ax) = plt.subplots(2,1)#, sharex=True)

for year in range(1880,2013):
    if year == 2012:
        ax[0].plot(range(339), ytd[year-1880,:339], c='red', label='2012')
    else:
        ax[0].plot(range(366), ytd[year-1880,:], c='tan')

ax[0].plot(range(366), ytd1931[:], c='b', label='1931')
ax[0].plot(range(338,366), ytdrL[338:], c='g', label='Record Cold')
ax[0].set_ylabel("YTD Average Temperature $^{\circ}\mathrm{F}$")
ax[0].set_xticks( (335,342,349,356,363))
ax[0].set_xticklabels( ('1 Dec', '7 Dec', '15 Dec', '22 Dec', '29 Dec'))
ax[1].set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax[1].set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax[0].grid(True)
ax[0].set_title("Chance of 2012 being Warmest Year on Record for Des Moines\nScenarios: append previous year time series to this year's YTD value\n%s/%s (%.1f%%) years (1880-2011) finish warmer than 1931" % (count, total,
                                                                    float(count) / float(total) * 100.0))
ax[0].set_xlim(334.5,364)
ax[0].set_ylim(52,59)
ax[0].legend(loc=3)

ax[1].plot(range(339), freq[:339], c='r', label='1931')
ax[1].grid(True)
ax[1].set_ylabel("Scenario Probability [%]")
ax[1].set_ylim(0,100)
ax[1].set_xlim(60,364)

plt.tight_layout()
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
