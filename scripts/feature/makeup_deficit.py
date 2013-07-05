import numpy
import iemdb
import datetime
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

# Get climatology
ccursor.execute("""
 SELECT sday, avg(precip) from alldata_ia where station = 'IA0000'
 GROUP by sday
""")
climate = {}
for row in ccursor:
    climate[ row[0] ] = float(row[1])
    
d365 = [0,]*365
running365 = []

(DOWN, UP) = range(2)

ccursor.execute("""
 SELECT day, precip, sday from alldata_ia where station = 'IA0000'
 and day > '1900-01-01' ORDER by day ASC
""")
phase = UP
peaks = []
makeuprate = []
ddays=[]
ratios = []
start = []
totals = []
for i, row in enumerate(ccursor):
    d = float(row[1]) - climate[ row[2] ]
    d365.pop()
    d365.insert(0, d )
    current = sum(d365)
    running365.append( current )
    if current < 0 and phase == UP: # We've gone negative
        phase = DOWN
        downturn = i
        downday = row[0]
    if current > 0 and phase == DOWN:
        phase = UP
        # 
        peakdeficit = min( running365[downturn:] )
        for j in range(downturn, len(running365)):
            if running365[j] == peakdeficit:
                if j == downturn:
                    break
                start.append( downday )
                peakdate = downday + datetime.timedelta(days=(j-downturn))
                total = i - downturn
                totals.append( total )
                days = i - j
                ratios.append( peakdeficit / float(days) )
                ddays.append(days)
                peaks.append( peakdeficit )
                makeuprate.append(0 - peakdeficit / float(days) )
                print peakdate, row[0], days, peakdeficit, peakdeficit / float(days)
                break

import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=10)

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
(fig, ax) = plt.subplots(3,1)

ax[0].scatter(peaks[:-1], makeuprate[:-1])
ax[0].scatter(peaks[-1], makeuprate[-1], marker='+', s=50, c='r', zorder=2)
ax[0].set_xlim(right=0.1)
ax[0].set_title("Iowa Statewide 365 Day Precipitation Deficits")
ax[0].set_ylim(bottom=0)
ax[0].set_ylabel("Rate [inch/day]")
ax[0].text(0.05, 0.7, "Recovery rate from\npeak deficit [inch]", transform=ax[0].transAxes,
           bbox=dict(fc='#FFFFFF'))
ax[0].grid(True)

ax[1].scatter(peaks[:-1], ddays[:-1])
ax[1].scatter(peaks[-1], ddays[-1], marker='+', s=50, c='r', zorder=2)
ax[1].set_yticks([0,91,182,273,365,365+91,365+181,365+273,365+365])
ax[1].set_ylabel("Days")
ax[1].set_xlabel("Peak Deficit [inch]")
ax[1].grid(True)
ax[1].set_ylim(bottom=0.1)
ax[1].set_xlim(right=0.1)
ax[1].text(0.75, 0.7, "Days to recover\nfrom peak deficit", transform=ax[1].transAxes,
           bbox=dict(fc='#FFFFFF'))

bars = ax[2].bar(start, peaks, width=totals, ec='tan', fc='tan')
bars[-1].set_facecolor('r')
bars[-1].set_edgecolor('r')
ax[2].set_xlim(datetime.datetime(1900,1,1), datetime.datetime(2014,1,1))
ax[2].grid(True)
ax[2].set_ylabel("Peak Deficit [inch]")

#plt.xticks(rotation=90)
#plt.subplots_adjust(bottom=.15)
fig.savefig('test.svg')
import iemplot
iemplot.makefeature('test')
