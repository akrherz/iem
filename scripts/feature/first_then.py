
import iemdb
import mx.DateTime
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
ccursor2 = COOP.cursor()

highs = []
doy = []

# Compute the first day each fall sub 32
ccursor.execute("""
    SELECT min(sday), year from alldata where stationid = 'ia0200'
    and month > 9 and high < 32 GROUP by year ORDER by year ASC
""")

for row in ccursor:
    sday = row[0]
    ts = mx.DateTime.strptime("2000"+sday, '%Y%m%d')
    
    year = row[1]
    ccursor2.execute("""
    select max(high) from alldata where stationid = 'ia0200'
    and year = %s and sday > %s
    """, (year, sday))
    row2 = ccursor2.fetchone()
    high = row2[0]
    if high is not None:
        highs.append( high )
        doy.append( int(ts.strftime("%j")))
    
import matplotlib.pyplot as plt
import iemplot

fig = plt.figure()
ax = fig.add_subplot(111)

ax.scatter( doy, highs)
ax.set_xticks( (295, 305, 312, 319, 326, 335, 342, 349) )
ax.set_xticklabels( ('Oct 22', 'Nov 1', 'Nov 8', 'Nov 15', 'Nov 22', 'Dec 1', 'Dec 8', 'Dec 15') )
ax.set_xlabel('Date of first fall day sub 32 $^{\circ}\mathrm{F}$')
ax.set_ylabel('Warmest Temperature till 31 December')
ax.set_title('Ames Fall High Temperature after Frozen Day')
ax.grid(True)
fig.savefig('test.ps')
iemplot.makefeature('test')