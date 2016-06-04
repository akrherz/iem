import numpy as np
import psycopg2
import datetime
import matplotlib.pyplot as plt
import matplotlib.colors as mpcolors
from pandas.io.sql import read_sql
import matplotlib.colorbar as mpcolorbar  # NOPEP8
import matplotlib.patheffects as PathEffects  # NOPEP8
from matplotlib.mlab import griddata

pgconn = psycopg2.connect(database='scada')


def make_colorbar(clevs, norm, cmap):
    """ Manual Color Bar """

    ax = plt.axes([0.92, 0.1, 0.05, 0.8], frameon=False,
                  yticks=[], xticks=[])

    under = clevs[0]-(clevs[1]-clevs[0])
    over = clevs[-1]+(clevs[-1]-clevs[-2])
    blevels = np.concatenate([[under, ], clevs, [over, ]])
    cb2 = mpcolorbar.ColorbarBase(ax, cmap=cmap,
                                  norm=norm,
                                  boundaries=blevels,
                                  extend='both',
                                  ticks=None,
                                  spacing='uniform',
                                  orientation='vertical')
    for i, lev in enumerate(clevs):
        y = float(i) / (len(clevs) - 1)
        fmt = '%g'
        txt = cb2.ax.text(0.5, y, fmt % (lev,), va='center', ha='center')
        txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                     foreground="w")])

    ax.yaxis.set_ticklabels([])
    ax.set_ylabel("Power Differential [kW]")


def do(turbine):
    df = read_sql("""
        WITH obs as (
            SELECT power, windspeed::int as ws, yawangle::int as yaw
            from data where turbine_id = %s
            and windspeed > 0 and windspeed < 12
            and alpha1 < 1 and yawangle >= 0),
        wsavg as (
            SELECT windspeed as ws, avg(power) from data WHERE alpha1 < 1
            and power > 0 GROUP by ws),
        agg as (
            SELECT avg(power), ws, yaw from obs GROUP by ws, yaw)

        SELECT a.avg - w.avg as pdiff, a.ws, a.yaw from agg a JOIN wsavg w
        ON (a.ws = w.ws)
        """, pgconn, params=(turbine, ), index_col=None)

    if len(df.index) < 10:
        print 'missing'
        return
    (fig, ax) = plt.subplots(2, 1, figsize=(10.24, 7.68))

    cmap = plt.cm.get_cmap('seismic')
    clevs = np.arange(-150, 151, 25)
    norm = mpcolors.BoundaryNorm(clevs, cmap.N)

    ax[0].scatter(df['yaw'], df['ws'], c=df['pdiff'], norm=norm,
                  edgecolor='None', marker='s', cmap=cmap)
    ax[0].set_xlim(0, 360)
    ax[0].set_xticks([0, 45, 90, 135, 180, 225, 270, 315, 360])
    ax[0].set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N'])
    ax[0].grid(True)
    ax[0].set_ylim(0, 12)
    ax[0].set_title(("Turbine %s Power Differential at Wind Speed\n"
                     "Pitch < 1$^\circ$"
                     ) % (turbine,))
    ax[0].set_ylabel("Wind Speed [mps]")
    ax[0].set_xlabel("Yaw Angle, Wind Direction [deg]")
    make_colorbar(clevs, norm, cmap)

    xi = np.linspace(0, 360, 360)
    yi = np.linspace(0, 12, 12)
    # grid the data.
    zi = griddata(df['yaw'], df['ws'], df['pdiff'], xi, yi, interp='linear')
    ax[1].contourf(xi, yi, zi, len(clevs), norm=norm, cmap=cmap)
    ax[1].set_xticks([0, 45, 90, 135, 180, 225, 270, 315, 360])
    ax[1].set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N'])
    ax[1].grid(True)
    ax[1].set_ylabel("Wind Speed [mps]")
    ax[1].set_xlabel("Yaw Angle, Wind Direction [deg]")

    fig.text(0.01, 0.02,
             "Generated: %s" % (
                    datetime.datetime.now().strftime("%d %b %Y %I:%M %p"),),
             fontsize=10)

    fig.savefig('powerdiff_%s.png' % (turbine,))
    plt.close()

for i in [136,]:
    print i
    do(i)
