"""
  Generate a simple scatter plot of power...
"""
import datetime
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mpcolors
import matplotlib.colorbar as mpcolorbar
import matplotlib.patheffects as PathEffects
from pyiem.meteorology import uv
from pyiem.datatypes import speed, direction
import numpy as np
import psycopg2
PGCONN = psycopg2.connect(database='mec', host='127.0.0.1', port='5555')
cursor = PGCONN.cursor()

def make_colorbar(clevs, norm, cmap):
    """ Manual Color Bar """

    ax = plt.axes([0.92, 0.1, 0.07, 0.8], frameon=False,
                      yticks=[], xticks=[])

    under = clevs[0]-(clevs[1]-clevs[0])
    over = clevs[-1]+(clevs[-1]-clevs[-2])
    blevels = np.concatenate([[under,], clevs, [over,]])
    cb2 = mpcolorbar.ColorbarBase(ax, cmap=cmap,
                                 norm=norm,
                                 boundaries=blevels,
                                 extend='both',
                                 ticks=None,
                                 spacing='uniform',
                                 orientation='vertical')
    for i, lev in enumerate(clevs):
        y = float(i) / (len(clevs) -1)
        fmt = '%g'
        txt = cb2.ax.text(0.5, y, fmt % (lev,), va='center', ha='center')
        txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                        foreground="w")])




def do(valid, frame):
    """ Generate plot for a given timestamp """
    
    cursor.execute("""select turbineid, power, ST_x(geom), ST_y(geom), yaw,
    windspeed 
     from sampled_data s JOIN turbines t on (t.id = s.turbineid) 
     WHERE valid = %s and power is not null and yaw is not null
     and windspeed is not null""", (valid,))
    lons = []
    lats = []
    vals = []
    u = []
    v = []
    for row in cursor:
        lons.append(row[2])
        lats.append(row[3])
        vals.append(row[1])
        a,b = uv(speed(row[5], 'MPS'), direction(row[4], 'deg'))
        u.append( a.value('MPS') )
        v.append( b.value('MPS') )
    vals = np.array(vals)
    avgv = np.average(vals)
    vals2 = vals - avgv
    print valid, min(vals2), max(vals2)
    (fig, ax) = plt.subplots(1,1)

    cmap = plt.cm.get_cmap('RdYlBu_r')
    cmap.set_under('white')
    
    cmap.set_over('black')
    clevs = np.arange(-300,301,50)
    norm = mpcolors.BoundaryNorm(clevs, cmap.N)
    ax.quiver(lons, lats, u, v, zorder=1)
    ax.scatter(lons, lats, c=vals2, vmin=-500, vmax=500,
               cmap=cmap, s=100, zorder=2)
    ax.set_title("Pomeroy Farm Turbine Power [kW] Diff from Farm Avg (1min sampled dataset)\nValid: %s" % (
                                                        valid.strftime("%d %b %Y %I:%M %p")))
    make_colorbar(clevs, norm, cmap)
    fig.savefig('power_movie/frame%05i.png' % (frame,))

    plt.close()

basets = datetime.datetime(2010,6,30, 20, 0)
for i in range(360):
    do( basets + datetime.timedelta(minutes=i), i)