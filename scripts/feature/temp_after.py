import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

highs = []
lows = []

for yr in range(1893,2011):
    ccursor.execute("""SELECT day, high from alldata where stationid = 'ia0200' and sday < '0218'
    and year = %s ORDER by high DESC, day DESC""", (yr,))
    row = ccursor.fetchone()
    high = row[1]
    ccursor.execute("""
    SELECT min(low) from alldata where stationid = 'ia0200' and day > %s and year = %s and month < 7
    """, (row[0], yr))
    row = ccursor.fetchone()
    low = row[0]
    
    highs.append( float(high) )
    lows.append( float(low) )
    
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)

ax.scatter(highs, lows)
ax.set_xlabel("Max Temperature prior to 17 Feb $^{\circ}\mathrm{F}$")
ax.set_ylabel("Min Temperature after Warmest $^{\circ}\mathrm{F}$")
ax.grid(True)
ax.set_title("Ames Coldest Temperature after Warmest Temperature\nprior to 17 Feb [1893-2010]")
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')