#!/usr/bin/env python
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
import cgi
import sys


def make_colorbar(clevs, norm, cmap):
    """ Manual Color Bar """

    ax = plt.axes([0.02, 0.1, 0.05, 0.8], frameon=False,
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

    ax.yaxis.set_ticklabels([])


def do(valid):
    """ Generate plot for a given timestamp """
    PGCONN = psycopg2.connect(database='mec', host='iemdb', port='5432',
                              user='mesonet')
    cursor = PGCONN.cursor()

    cursor.execute("""select turbineid, power, ST_x(geom), ST_y(geom), yaw,
    windspeed, pitch
     from sampled_data s JOIN turbines t on (t.id = s.turbineid) 
     WHERE valid = %s and power is not null and yaw is not null
     and windspeed is not null and pitch is not null""", (valid,))
    lons = []
    lats = []
    vals = []
    u = []
    v = []
    ws = []
    yaw = []
    pitch = []
    for row in cursor:
        lons.append(row[2])
        lats.append(row[3])
        vals.append(row[1])
        ws.append( row[5] )
        yaw.append( row[4])
        a,b = uv(speed(row[5], 'MPS'), direction(row[4], 'deg'))
        u.append( a.value('MPS') )
        v.append( b.value('MPS') )
        pitch.append(row[6])
    vals = np.array(vals)
    avgv = np.average(vals)
    #vals2 = vals - avgv
    fig = plt.figure(figsize=(12.8,7.2))
    ax = fig.add_axes([0.14, 0.1, 0.52, 0.8])

    cmap = plt.cm.get_cmap('jet')
    cmap.set_under('tan')
    cmap.set_over('black')
    clevs = np.arange(0,1501,100)
    norm = mpcolors.BoundaryNorm(clevs, cmap.N)
    ax.quiver(lons, lats, u, v, zorder=1)
    ax.scatter(lons, lats, c=vals, norm=norm, edgecolor='none',
               cmap=cmap, s=100, zorder=2)
    ax.set_title("Pomeroy Farm Turbine Power [kW] (1min sampled dataset)\nValid: %s" % (
                                                        valid.strftime("%d %b %Y %I:%M %p")))
    make_colorbar(clevs, norm, cmap)
    
    ax.text(0.05, 0.05, "Turbine Avg: %.1f kW" % (avgv,),
            transform=ax.transAxes)
    ax.set_xlabel("Longitude $^\circ$E")
    ax.set_ylabel("Latitude $^\circ$N")
    
    # Next plot
    ax2 = fig.add_axes([0.7, 0.73, 0.28, 0.25])
    ax2.scatter(ws, vals)
    ax2.text(0.5, -0.2, "Wind Speed $ms^{-1}$", transform=ax2.transAxes,
             ha='center')
    #ax2.set_ylabel("Power kW")
    ax2.grid(True)

    # Next plot
    ax3 = fig.add_axes([0.7, 0.41, 0.28, 0.25], sharey=ax2)
    ax3.scatter(yaw, vals)
    ax3.text(0.5, -0.2, "Yaw $^\circ$N", transform=ax3.transAxes, ha='center')
    #ax3.set_ylabel("Power kW")
    ax3.set_xlim(0,360)
    ax3.set_xticks(np.arange(0,361,45))
    ax3.grid(True)
    
    # Next plot
    ax4 = fig.add_axes([0.7, 0.08, 0.28, 0.25], sharey=ax2)
    ax4.scatter(pitch, vals)
    ax4.text(0.5, -0.2, "Pitch $^\circ$", transform=ax4.transAxes, ha='center')
    ax4.grid(True)
    ax4.set_ylim(bottom=-10)
    ax4.set_xlim(-5,12)
    
    plt.savefig( sys.stdout )


if __name__ == '__main__':
    # Go main Go
    form = cgi.FieldStorage()
    ts = form.getfirst('ts', '200006302000')
    ts = datetime.datetime.strptime(ts, '%Y%m%d%H%M')
    sys.stdout.write("Content-type: image/png\n\n")
    do(ts)