import iemdb
import numpy.ma
MOS = iemdb.connect('mos', bypass=True)
mcursor = MOS.cursor()
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

# Get rain obs
obs = {}
ccursor.execute("""
    SELECT day, precip from alldata_ia where year > 2003 and 
    month = 5 and station = 'IA2203' and precip > 0.001
""")
for row in ccursor:
    obs[ row[0].strftime("%Y%m%d") ] = row[1]
    
# Get pwater
mcursor.execute("""
    SELECT runtime, pwater from model_gridpoint where station = 'KDSM'
    and model = 'NAM' and runtime = ftime and extract(month from runtime) = 5 
    and extract(hour from runtime) = 7
""")
total = numpy.ma.zeros( (20,), 'f') # 4 mm to 100
hits = numpy.ma.zeros( (20,), 'f')
pwater = []
precip = []
for row in mcursor:
    bin = int(row[1] / 4)
    print row[1], bin
    if obs.has_key( row[0].strftime("%Y%m%d")):
        hits[bin] += 1
    total[bin] += 1
    pwater.append( row[1] )
    precip.append( obs.get(row[0].strftime("%Y%m%d"), 0) )
    
import matplotlib.pyplot as plt

fig, ax = plt.subplots(2, 1)
hits.mask = numpy.where(hits == 0, True, False)
total.mask = numpy.where(total == 0, True, False)
climate = numpy.ma.sum(hits) / numpy.ma.sum(total) * 100.0
print total
percent = hits / total * 100.0
bars = ax[0].bar( numpy.arange(0,80,4), percent, width=4.0 ,
                  facecolor='lightblue')
ax[0].plot([0,51], [climate, climate], color='b')
ax[0].text(5, climate + 3, 'Climatology', color='b')
for i in range(len(bars)):
    if total[i] > 0:
        ax[0].text( i * 4 + 2, percent[i] - 7 , "%.0f" % (total[i],),
                    ha='center')
ax[0].text(5, 80, 'Bar label is \n# of days')
ax[0].set_title("Des Moines May Precipitable Water & Rainfall (2004-2012)\n7 AM NAM model analysis and daily rainfall frequency")
ax[0].set_ylabel("Measurable Daily Precip[%]")
ax[1].set_xlabel("Preciptable Water [inch]")
ax[0].set_xticks(numpy.arange(0,2*25.5, 25.4/4.0))
ax[0].set_xticklabels(numpy.arange(0,2.1,0.25))
ax[0].grid(True)
ax[0].set_xlim(0,51)

ax[1].scatter( pwater, precip )
ax[1].set_xticks(numpy.arange(0,2*25.5, 25.4/4.0))
ax[1].set_xticklabels(numpy.arange(0,2.1,0.25))
ax[1].set_ylim(-0.1, 3.5)
ax[1].set_ylabel("Daily Precipitation [inch]")
ax[1].plot([0,2*25.4], [0,2])
ax[1].grid(True)
ax[1].set_xlim(0,51)


fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')