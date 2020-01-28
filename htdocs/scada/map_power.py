"""
  Generate a simple scatter plot of power...
"""
from io import BytesIO
import datetime

import numpy as np
import matplotlib.colors as mpcolors
import matplotlib.colorbar as mpcolorbar
import matplotlib.patheffects as PathEffects
from paste.request import parse_formvars
from pyiem.meteorology import uv
from pyiem.plot.use_agg import plt
from pyiem.datatypes import speed, direction
from pyiem.util import get_dbconn


def make_colorbar(clevs, norm, cmap):
    """ Manual Color Bar """

    ax = plt.axes([0.02, 0.1, 0.05, 0.8], frameon=False, yticks=[], xticks=[])

    under = clevs[0] - (clevs[1] - clevs[0])
    over = clevs[-1] + (clevs[-1] - clevs[-2])
    blevels = np.concatenate([[under], clevs, [over]])
    cb2 = mpcolorbar.ColorbarBase(
        ax,
        cmap=cmap,
        norm=norm,
        boundaries=blevels,
        extend="both",
        ticks=None,
        spacing="uniform",
        orientation="vertical",
    )
    for i, lev in enumerate(clevs):
        y = float(i) / (len(clevs) - 1)
        fmt = "%g"
        txt = cb2.ax.text(0.5, y, fmt % (lev,), va="center", ha="center")
        txt.set_path_effects(
            [PathEffects.withStroke(linewidth=2, foreground="w")]
        )

    ax.yaxis.set_ticklabels([])


def do(valid):
    """ Generate plot for a given timestamp """
    pgconn = get_dbconn("scada")
    cursor = pgconn.cursor()

    cursor.execute(
        """select turbine_id, power, lon, lat,
    yawangle, windspeed, alpha1
     from data s JOIN turbines t on (t.id = s.turbine_id)
     WHERE valid = %s and power is not null and yawangle is not null
     and windspeed is not null and alpha1 is not null""",
        (valid,),
    )
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
        ws.append(row[5])
        yaw.append(row[4])
        a, b = uv(speed(row[5], "MPS"), direction(row[4], "deg"))
        u.append(a.value("MPS"))
        v.append(b.value("MPS"))
        pitch.append(row[6])
    pitch = np.array(pitch)
    vals = np.array(vals)
    avgv = np.average(vals)
    # vals2 = vals - avgv
    fig = plt.figure(figsize=(12.8, 7.2))
    ax = fig.add_axes([0.14, 0.1, 0.52, 0.8])

    cmap = plt.cm.get_cmap("jet")
    cmap.set_under("tan")
    cmap.set_over("black")
    # cmap = plt.cm.get_cmap('seismic')
    # clevs = np.arange(-250, 251, 50)
    clevs = np.arange(0, 1501, 150)
    norm = mpcolors.BoundaryNorm(clevs, cmap.N)
    ax.quiver(lons, lats, u, v, zorder=1)
    ax.scatter(
        lons,
        lats,
        c=vals,
        norm=norm,
        edgecolor="none",
        cmap=cmap,
        s=100,
        zorder=2,
    )
    ax.get_yaxis().get_major_formatter().set_useOffset(False)
    ax.get_xaxis().get_major_formatter().set_useOffset(False)
    ax.xaxis.set_major_formatter(plt.NullFormatter())
    ax.yaxis.set_major_formatter(plt.NullFormatter())
    ax.set_title(
        ("Turbine Power [kW]\n" "Valid: %s")
        % (valid.strftime("%d %b %Y %I:%M %p"))
    )
    make_colorbar(clevs, norm, cmap)

    ax.text(
        0.05,
        0.05,
        "Turbine Power: $\mu$= %.1f $\sigma$= %.1f kW" % (avgv, np.std(vals)),
        transform=ax.transAxes,
    )
    ax.text(
        0.05,
        0.01,
        "Wind $\mu$= %.1f $\sigma$= %.1f $ms^{-1}$"
        % (np.average(ws), np.std(ws)),
        transform=ax.transAxes,
    )
    ax.set_xlabel("Longitude $^\circ$E")
    ax.set_ylabel("Latitude $^\circ$N")
    ax.set_xlim(-93.475, -93.328)
    ax.set_ylim(42.20, 42.31)

    # Next plot
    ax2 = fig.add_axes([0.7, 0.80, 0.28, 0.18])
    ax2.scatter(ws, vals, edgecolor="k", c="k")
    ax2.text(
        0.5,
        -0.25,
        "Wind Speed $ms^{-1}$",
        transform=ax2.transAxes,
        ha="center",
    )
    ax2.set_xlim(0, 20)
    # ax2.set_ylabel("Power kW")
    ax2.grid(True)

    # Next plot
    ax3 = fig.add_axes([0.7, 0.57, 0.28, 0.18], sharey=ax2)
    ax3.scatter(yaw, vals, edgecolor="k", c="k")
    ax3.text(0.5, -0.25, "Yaw", transform=ax3.transAxes, ha="center")
    # ax3.set_ylabel("Power kW")
    ax3.set_xlim(0, 360)
    ax3.set_xticks(np.arange(0, 361, 45))
    ax3.set_xticklabels(["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"])
    ax3.grid(True)

    # Next plot
    ax4 = fig.add_axes([0.7, 0.32, 0.28, 0.18], sharey=ax2)
    ax4.scatter(pitch, vals, edgecolor="k", c="k")
    ax4.text(
        0.5, -0.25, "Pitch $^\circ$", transform=ax4.transAxes, ha="center"
    )
    ax4.set_ylim(-10, 1600)
    ax4.grid(True)

    # Next plot
    ax5 = fig.add_axes([0.7, 0.07, 0.28, 0.18], sharex=ax4)
    ax5.scatter(pitch, ws, edgecolor="k", c="k")
    ax5.text(
        0.5, -0.25, "Pitch $^\circ$", transform=ax5.transAxes, ha="center"
    )
    ax5.grid(True)
    ax5.set_ylim(bottom=-10)
    # maxpitch = max(np.where(pitch > 20, 0, pitch))
    # ax5.set_xlim(np.ma.minimum(pitch)-0.5, maxpitch+0.5)
    ax5.set_xlim(-3, 20.1)
    ax5.set_ylim(0, 20)
    ax5.text(
        -0.1,
        0.5,
        "Wind Speed $ms^{-1}$",
        transform=ax5.transAxes,
        ha="center",
        va="center",
        rotation=90,
    )


def application(environ, start_response):
    """Go Main Go."""
    form = parse_formvars(environ)
    ts = form.get("ts", "200006302000")
    ts = datetime.datetime.strptime(ts, "%Y%m%d%H%M")
    # yawsource = form.get("yawsource", "yaw")
    headers = [("Content-type", "image/png")]
    start_response("200 OK", headers)
    do(ts)
    bio = BytesIO()
    plt.savefig(bio)
    return [bio.getvalue()]
