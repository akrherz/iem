import iemdb
import iemplot
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()
snowdlats = []
snowdlons = []
snowdvals = []
icursor.execute("""
    SELECT x(geom), y(geom), snowd from summary_2010 WHERE
    network in ('IA_COOP','MO_COOP','IL_COOP', 'WI_COOP',
    'MN_COOP', 'NE_COOP', 'SD_COOP', 'KS_COOP') and 
    snowd >= 0 and day = '2010-12-30'
""")
for row in icursor:
    snowdlats.append( row[1] )
    snowdlons.append( row[0] )
    snowdvals.append( row[2] )
    
highslats = []
highslons = []
highsvals = []
icursor.execute("""
    SELECT x(geom), y(geom), max_dwpf, station from summary_2010 WHERE
    network in ('IA_ASOS','AWOS') 
    and max_tmpf > 0 and day = '2010-12-30'
""")
for row in icursor:
    print row
    highslats.append( row[1] )
    highslons.append( row[0] )
    highsvals.append( row[2] )
    
# Grid please
snowd, res = iemplot.grid_iowa(snowdlons, snowdlats, snowdvals)
highs, res = iemplot.grid_iowa(highslons, highslats, highsvals)

import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111)

#ax.imshow( highs )
ax.scatter( snowd[2:-2,2:-2].flatten(), highs[2:-2,2:-2].flatten() )
ax.set_xlim(0,25)
ax.set_xlabel('Morning Snow Depth [inch]')
ax.set_ylabel('Afternoon High Dew Point [F]')
ax.set_title("30 Dec 2010: High Dew Point  vs. Snow Depth\nAnalysis over Iowa")
ax.grid(True)

fig.savefig('test.png')
#iemplot.makefeature('test')
