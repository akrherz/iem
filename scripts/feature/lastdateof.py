# Produce a plot of the last day of the year at a given temperature

import mx.DateTime
import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

# get climatology
ccursor.execute("""SELECT valid, high from ncdc_climate71 where station = 'ia0200'
    ORDER by valid ASC""")
climate = []
cdoy = []
for row in ccursor:
    ts = row[0]
    climate.append( row[1] )
    cdoy.append( int(ts.strftime("%j")) )

# Extract obs
ccursor.execute("""SELECT sday, high from alldata where stationid = 'ia0200'
    and year = 2010 ORDER by day ASC""")
obs = []
odoy = []
for row in ccursor:
    ts = mx.DateTime.strptime("2010%s" % (row[0],) ,'%Y%m%d' )
    obs.append( row[1] )
    odoy.append( int(ts.strftime("%j")) )

ccursor.execute("""SELECT sday, high from alldata where stationid = 'ia0200'
    and year = 2009 ORDER by day ASC""")
obs2009 = []
odoy2009 = []
for row in ccursor:
    ts = mx.DateTime.strptime("2009%s" % (row[0],) ,'%Y%m%d' )
    obs2009.append( row[1] )
    odoy2009.append( int(ts.strftime("%j")) )

ccursor.execute("""select high, max(sday) from alldata where stationid = 'ia0200' 
    GROUP by high ORDER by high DESC""")

highs = []
doy = []
m = 0
for row in ccursor:
    if row[0] <= 50:
        continue
    ts = mx.DateTime.strptime("2009%s" % (row[1],) ,'%Y%m%d' )
    highs.append( row[0] )
    if int( ts.strftime("%j") ) > m:
        m = int( ts.strftime("%j") )
    doy.append( m )
    
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

fig = plt.figure()
ax = fig.add_subplot(111)




ax.plot( doy, highs , label='Latest Occurence', zorder=2)
ax.scatter( odoy, obs , label='2010 Obs', zorder=2)
ax.scatter( odoy2009, obs2009 , label='2009 Obs', marker='+', zorder=2)
ax.plot( cdoy, climate, label='Climatology' )
ax.grid(True)

ax.set_xticks( (1,32,60,91,121,152,182,213,244,258,274,289,305,319,335,349,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep 1','Sep 15', 'Oct 1','Oct 15', 'Nov 1','Nov 15', 'Dec 1', 'Dec 15') )
ax.set_xlim( 240, 366 )
ax.set_ylim( 50, 110)
ax.set_ylabel("Temperature $^{\circ}\mathrm{F}$")
ax.set_xlabel('Day of Year')
ax.set_title("Ames High Temperatures [1893-2010]")

rect = Rectangle((274, 50), 31, 70, facecolor="#aaaaaa", zorder=1)
ax.add_patch(rect)

ax.legend()
import iemplot
fig.savefig('test.ps')
iemplot.makefeature('test')