import psycopg2
import matplotlib.pyplot as plt
from pandas.io.sql import read_sql
import pandas as pd

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

    select classify as tod,
    (yawangle / 5)::int * 5 as yaw, avg(wdiff) as avg_wdiff,
    avg(pdiff) as avg_pdiff, count(*) from
    combo c JOIN stability s on (c.valid = s.valid)
    GROUP by tod, yaw ORDER by yaw ASC
    """, pgconn, params=(turbine_id, ), index_col=None)
    if len(df.index) == 0:
        return

    (fig, ax) = plt.subplots(2, 1)

    ax[0].set_title("Turbine %s Bias from Wind Farm Average by Yaw Angle" % (
                                                                turbine_id,))
    for c in ['STABLE', 'NEUTRAL', 'UNSTABLE']:
        df2 = df[df['tod'] == c]
        ax[0].step(df2['yaw'], df2['avg_wdiff'], lw=2,
                   label=c)
    ax[0].set_xlim(0, 360)
    ax[0].set_xticks([0, 45, 90, 135, 180, 225, 270, 315, 360])
    ax[0].set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N'])
    ax[0].set_ylim(-2.5, 2.5)
    ax[0].set_ylabel("Wind Speed Diff [mps]")
    ax[0].grid(True)
    ax[0].set_xlabel("Yaw [deg N]")
    ax[0].legend(loc=3, ncol=3, fontsize=10)

    for c in ['STABLE', 'NEUTRAL', 'UNSTABLE']:
        df2 = df[df['tod'] == c]
        ax[1].step(df2['yaw'], df2['avg_pdiff'], lw=2,
                   label=c)
    ax[1].set_xlim(0, 360)
    ax[1].set_xticks([0, 45, 90, 135, 180, 225, 270, 315, 360])
    ax[1].set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N'])
    ax[1].set_ylim(-350, 350)
    ax[1].set_ylabel("Power Difference [kW]")
    ax[1].grid(True)
    ax[1].set_xlabel("Yaw [deg N]")
    ax[1].legend(loc=3, ncol=3, fontsize=10)

    fig.savefig("yaw_bias_%s_stability.png" % (turbine_id,))
    plt.close()

    writer = pd.ExcelWriter('pdiff_%s.xlsx' % (turbine_id,),
                            engine='xlsxwriter')

    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()

for i in range(101, 184):
    print i
    do(i)
