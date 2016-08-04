import psycopg2
import matplotlib.pyplot as plt
from pandas.io.sql import read_sql

pgconn = psycopg2.connect(database='scada')

df = read_sql("""
    SELECT power, windspeed from data where alpha1 < 1
    and power > 0 and windspeed > 0 and turbine_id = 141
    """, pgconn, index_col=None)

(fig, ax) = plt.subplots(1, 1)

ax.set_title(("Wind Farm Normalized Power\n"
              "[Turbine 141, alpha1 blade pitch < 1]"))

ax.scatter(df['windspeed'].values, df['power'] / 1500., facecolor='b',
           edgecolor='None', alpha=0.1)
ax.set_xlim(left=0)
ax.set_ylim(bottom=0)
ax.grid(True)
ax.set_ylabel("Normalized Power")
ax.set_xlabel("Nacelle Wind Speed - m s$^{-1}$")

fig.savefig('norm_power_141.png')
