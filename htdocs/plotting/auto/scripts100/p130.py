"""temps vs high and low"""

import numpy as np
from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """This chart displays the average high and low
    temperature by month for days with or without snowcover reported.  There
    are a number of caveats due to the timing of the daily temperature and
    snow cover report.  Also with the quality of the snow cover data."""
    desc['arguments'] = [
        dict(type='station', name='station', default='IATDSM',
             label='Select Station:', network='IACLIMATE'),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('coop')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station'].upper()
    table = "alldata_%s" % (station[:2], )
    nt = NetworkTable("%sCLIMATE" % (station[:2],))
    df = read_sql("""
    SELECT year, month,
    avg(high) as avg_high_all, avg(low) as avg_low_all,
    avg(case when snowd > 0 then high else null end) as avg_high_snow,
    avg(case when snowd > 0 then low else null end) as avg_low_snow,
    avg(case when snowd = 0 then high else null end) as avg_high_nosnow,
    avg(case when snowd = 0 then low else null end) as avg_low_nosnow,
    sum(case when snowd > 0 then 1 else 0 end) as coverdays
    from """ + table + """
    WHERE station = %s
    GROUP by year, month
    """, pgconn, params=(station, ), index_col=None)

    # Only use months that had at least one day of snowcover
    df2 = df[df['coverdays'] > 0]
    df3 = df2.groupby('month').mean()

    (fig, ax) = plt.subplots(2, 1)
    for i, lbl in enumerate(['high', 'low']):
        ys = df3.loc[[11, 12, 1, 2, 3], 'avg_%s_nosnow' % (lbl, )]
        ax[i].bar(np.arange(5) - 0.2, ys.values, width=0.4, align='center',
                  label='Without Snowcover', fc='brown', zorder=4)
        for x, y in enumerate(ys):
            ax[i].text(x - 0.2, y + 2, "%.0f" % (y, ), ha='center',
                       color='brown')

        ys2 = df3.loc[[11, 12, 1, 2, 3], 'avg_%s_snow' % (lbl, )]
        ax[i].bar(np.arange(5) + 0.2, ys2.values, width=0.4, align='center',
                  label='With Snowcover', fc='blue', zorder=4)
        for x, y in enumerate(ys2):
            ax[i].text(x + 0.2, y + 2, "%.0f" % (y, ), ha='center',
                       color='blue')

        ys3 = df3.loc[[11, 12, 1, 2, 3], 'avg_%s_all' % (lbl, )]
        ax[i].scatter(np.arange(5), ys3.values, marker='s', s=50, zorder=5,
                      label='Overall', c='yellow')
        for x, y in enumerate(ys3):
            ax[i].text(x - 0.05, y, "%.0f" % (y, ), ha='right', zorder=6,
                       va='top', color='yellow')
        ax[i].set_xticks(range(5))
        ax[i].set_xticklabels(['Nov', 'Dec', 'Jan', 'Feb', 'Mar'])
        ax[i].legend(ncol=3, fontsize=10)
        ax[i].grid(True)
        ax[i].set_ylim([(ys2.min() - 10), (ys.max() + 20)])

    ax[0].set_title(("%s [%s]\nSnow Cover Impact on Average Temp [%s-%s]"
                     ) % (nt.sts[station]['name'], station,
                          df2['year'].min(), df2['year'].max()))
    ax[0].set_ylabel(r"Avg High Temp $^\circ$F")
    ax[1].set_ylabel(r"Avg Low Temp $^\circ$F")

    return fig, df


if __name__ == '__main__':
    plotter(dict())
