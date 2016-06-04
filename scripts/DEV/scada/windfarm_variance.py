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

df = read_sql("""
    WITH wfavg as (
        SELECT valid, avg(windspeed) as ws from data GROUP by valid),
    obs as (
        SELECT d.valid, w.ws as ws2, (d.yawangle / 15)::int * 15 as yaw2,
        d.windspeed, d.power from data d JOIN wfavg w
        on (d.valid = w.valid) WHERE windspeed > 0 and yawangle is not null
        and alpha1 < 1)

    SELECT ws2::int as ws, yaw2::int as yaw, avg(power) as p
    from obs GROUP by ws, yaw
    """, pgconn, index_col=None)

cmap = plt.cm.get_cmap('jet')
cmap.set_under('white')
cmap.set_over('k')
clevs = np.arange(0, 1500.1, 150)
norm = mpcolors.BoundaryNorm(clevs, cmap.N)

(fig, ax) = plt.subplots(1, 1)

ax.set_title(("Variance in Turbine Reported Power"))

xi = np.linspace(0, 360, 360)
yi = np.linspace(0, 12, 12)
# grid the data.
zi = griddata(df['yaw'], df['ws'], df['p'], xi, yi, interp='linear')
res = ax.contourf(xi, yi, zi, len(clevs), norm=norm, cmap=cmap)
fig.colorbar(res, extend='both')
ax.set_xticks([0, 45, 90, 135, 180, 225, 270, 315, 360])
ax.set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N'])
ax.grid(True)
ax.set_ylabel("Farm Ave Wind Speed [mps]")
ax.set_xlabel("Turbine Yaw Direction [deg N]")

fig.savefig('test.png')
