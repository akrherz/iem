import numpy
from matplotlib import pyplot as plt
import iemdb
from scipy import stats
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

sql = """
    select year, 
    sum(case when month in (5,6) then precip else 0 end), 
    sum(case when month in (7) then sdd86(high,low) else 0 end) 
    from alldata_ia
    where station = 'IA1319' and month in (5,6,7,8) 
    GROUP by year ORDER by year ASC
""" 
ccursor.execute(sql)
gdd = []
precip = []
years = []
for row in ccursor:
    years.append( row[0] )
    gdd.append( float(row[2]) )
    precip.append( float(row[1]) )

gdd[-1] += 11

fig = plt.figure()
ax = fig.add_subplot(111)

ax.scatter(gdd[:-1], precip[:-1], c='r')
#ax.text(gdd[-1] + 3, precip[-1] + 0.2, "2012")
for yr1, gdd1, p in zip(years, gdd, precip):
    if yr1 == 2012:
        continue
    if gdd1 > 160 or p < 4:
        dy = 0.1
        if yr1 in [1913,1896,1963]:
            dy = 0.3
        if yr1 in [1933,2012]:
            dy = -0.2
        ax.text(gdd1 + 3, p - dy, "%s" % (yr1,))
ax.set_xlabel("July Stress Degree Days (base 86$^{\circ}\mathrm{F}$)")
ax.set_ylabel("May June Precipitation [inch]")
ax.set_title("Cedar Rapids May - August Precipitation & SSDs")
ax.set_xlim(-0.5, max(gdd)+30)
ax.grid(True)

fig.savefig("test.ps")
import iemplot
iemplot.makefeature("test")
#plt.savefig("test.png")
