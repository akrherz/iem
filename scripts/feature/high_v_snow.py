import iemdb
import iemplot
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()
snowdlats = []
snowdlons = []
snowdvals = []
icursor.execute("""
    SELECT ST_x(geom), ST_y(geom), snowd from summary_2014 s JOIN stations t 
    ON (t.iemid = s.iemid) WHERE
    network in ('IA_COOP') and 
    snowd >= 0 and day = '2014-03-10'
""")
for row in icursor:
    snowdlats.append( row[1] )
    snowdlons.append( row[0] )
    snowdvals.append( row[2] )
    
highslats = []
highslons = []
highsvals = []
icursor.execute("""
    SELECT ST_x(geom), ST_y(geom), max_tmpf, id from summary_2014 s JOIN stations t
    on (t.iemid = s.iemid) WHERE
    network in ('IA_ASOS','AWOS') 
    and max_tmpf > 0 and day = '2014-03-10' ORDER by max_tmpf ASC
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
ax.set_xlim(-0.3,30)
ax.set_xlabel('Morning Snow Depth [inch]')
ax.set_ylabel('Afternoon High Temperature [F]')
ax.set_title("10 Mar 2014: High Temperature  vs. Snow Depth\nPoint Comparison of Gridded Analysis over Iowa")
ax.grid(True)

fig.savefig('test.ps')
iemplot.makefeature('test')
