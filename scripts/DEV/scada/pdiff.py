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


def do(turbine_id):
    #
    df = read_sql("""
    with wfavg as (
        SELECT valid, avg(windspeed) as ws, avg(power) as p from data
        GROUP by valid),
    combo as (
        SELECT d.valid, d.yawangle, d.windspeed - w.ws as wdiff,
        d.power - w.p as pdiff
        from wfavg w, data d WHERE w.valid = d.valid and d.turbine_id = %s
        and d.yawangle is not null and d.windspeed is not null
    )

    select (yawangle / 5)::int * 5 as yaw, avg(wdiff) as avg_wdiff,
    avg(pdiff) as avg_pdiff from combo GROUP by yaw ORDER by yaw ASC
    """, pgconn, params=(turbine_id, ), index_col=None)
    if len(df.index) == 0:
        return

    (fig, ax) = plt.subplots(2, 1)

    ax[0].set_title("Turbine %s Bias from Wind Farm Average by Yaw Angle" % (
                                                                turbine_id,))
    ax[0].bar(df['yaw'], df['avg_wdiff'], width=5)
    ax[0].set_xlim(0, 360)
    ax[0].set_xticks([0, 45, 90, 135, 180, 225, 270, 315, 360])
    ax[0].set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N'])
    ax[0].set_ylim(-2, 2)
    ax[0].set_ylabel("Wind Speed Diff [mps]")
    ax[0].grid(True)
    ax[0].set_xlabel("Yaw [deg N]")

    ax[1].bar(df['yaw'], df['avg_pdiff'], width=5)
    ax[1].set_xlim(0, 360)
    ax[1].set_xticks([0, 45, 90, 135, 180, 225, 270, 315, 360])
    ax[1].set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N'])
    ax[1].set_ylim(-250, 250)
    ax[1].set_ylabel("Power Difference [kW]")
    ax[1].grid(True)
    ax[1].set_xlabel("Yaw [deg N]")

    fig.savefig("yaw_bias_%s.png" % (turbine_id,))
    plt.close()

for i in range(101, 184):
    print i
    do(i)
