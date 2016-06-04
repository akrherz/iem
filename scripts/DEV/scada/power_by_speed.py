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
    df = read_sql("""
    WITH wfavg as (
     SELECT valid, avg(windspeed) as ws2 from data 
     WHERE windspeed > 0 GROUP by valid)

    SELECT w.ws2::int as ws, (yawangle  / 5)::int * 5 as yaw, avg(power) as p
    from data d JOIN wfavg w on (d.valid = w.valid) WHERE turbine_id = %s and yawangle is not null and power is not null
    and windspeed is not null and alpha1 < 1 GROUP by ws, yaw ORDER by yaw ASC
    """, pgconn, params=(turbine_id, ), index_col=None)
    if len(df.index) == 0:
        return

    (fig, ax) = plt.subplots(1, 1)

    for ws in range(1, 10, 2):
        df2 = df[df['ws']==ws]
        ax.plot(df2['yaw'], df2['p'], label=str(ws))

    ax.set_title(("Turbine %s Avg Power at Farm Avg Wind Speed [mps] by Yaw\n"
                  "For alpha1 < 1 $^\circ$F") % (turbine_id,))

    ax.set_xticks([0, 45, 90, 135, 180, 225, 270, 315, 360])
    ax.set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N'])
    ax.grid(True)
    ax.set_ylabel("Power [kW]")
    ax.set_xlim(0, 360)
    ax.set_ylim(0, 1500)
    ax.set_xlabel("Turbine Yaw Direction [deg N]")
    ax.legend(ncol=5)

    fig.savefig('wf_avgpower_by_yaw_%s.png' % (turbine_id,))
    plt.close()

for i in range(101, 184):
    print i
    do(i)
