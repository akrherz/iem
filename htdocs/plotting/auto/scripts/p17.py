"""Generate monthly high/low climo plot"""
import datetime
import warnings

import numpy as np
import psycopg2
from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
from pyiem.util import get_autoplot_context

warnings.simplefilter("ignore", UserWarning)


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['cache'] = 300
    today = datetime.date.today()
    mo = today.month
    yr = today.year
    desc['data'] = True
    desc['description'] = """Daily plot of observed high and low temperatures
    along with the daily climatology for the nearest (sometimes same) location.
    """
    desc['arguments'] = [
        dict(type='zstation', name='station', default='AMW', network='IA_ASOS',
             label='Select Station:'),
        dict(type="month", name="month", default=mo, label="Select Month"),
        dict(type="year", name="year", default=yr, label="Select Year",
             minvalue=2000),
    ]
    return desc


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.patheffects as PathEffects
    from matplotlib.patches import Rectangle
    pgconn_iem = psycopg2.connect(database='iem', host='iemdb', user='nobody')
    pgconn_coop = psycopg2.connect(database='coop', host='iemdb',
                                   user='nobody')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    network = ctx['network']
    year = ctx['year']
    month = ctx['month']
    nt = NetworkTable(network)

    table = "summary_%s" % (year,)

    sts = datetime.date(year, month, 1)
    ets = sts + datetime.timedelta(days=35)
    ets = ets.replace(day=1)

    days = int((ets - sts).days)
    weekends = []
    now = sts
    while now < ets:
        if now.weekday() in [5, 6]:
            weekends.append(now.day)
        now += datetime.timedelta(days=1)

    df = read_sql("""
    SELECT day, max_tmpf, min_tmpf,
    extract(day from day) as day_of_month
    from """+table+""" s JOIN stations t
    on (t.iemid = s.iemid) WHERE id = %s and network = %s and
    day >= %s and day < %s ORDER by day ASC
    """, pgconn_iem,  params=(station, network, sts, ets),
                  index_col='day_of_month')
    has_data = (df['max_tmpf'].max() > -90)

    # Get the normals
    cdf = read_sql("""
    SELECT valid, high, low,
    extract(day from valid) as day_of_month from
    ncdc_climate81 where station = %s
    and extract(month from valid) = %s ORDER by valid ASC
    """, pgconn_coop, params=(nt.sts[station]['ncdc81'], month),
                   index_col='day_of_month')

    if len(cdf.index) > 0:
        df = cdf.join(df)
        has_climo = True
    else:
        df['high'] = None
        df['low'] = None
        has_climo = False
    (fig, ax) = plt.subplots(1, 1)

    for day in weekends:
        rect = Rectangle([day-0.5, -100], 1, 300, facecolor='#EEEEEE',
                         edgecolor='None')
        ax.add_patch(rect)

    if has_climo:
        ax.plot(df.index.values, df['high'].values, zorder=3, marker='o',
                color='pink')
        ax.plot(df.index.values, df['low'].values, zorder=3, marker='o',
                color='skyblue')
    if has_data:
        ax.bar(df.index.values - 0.3, df['max_tmpf'].values,
               fc='r', ec='k', width=0.3,
               linewidth=0.6)
        ax.bar(df.index.values, df['min_tmpf'].values,
               fc='b', ec='k', width=0.3,
               linewidth=0.6)
    else:
        ax.text(0.5, 0.5, "No Data Found", transform=ax.transAxes,
                ha='center')
        ax.set_ylim(0, 1)

    i = 0
    if has_data:
        for _, row in df.iterrows():
            if np.isnan(row['max_tmpf']) or np.isnan(row['min_tmpf']):
                i += 1
                continue
            txt = ax.text(i+1-0.15, row['max_tmpf']+0.5,
                          "%.0f" % (row['max_tmpf'],),
                          fontsize=10, ha='center', va='bottom', color='k')
            txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                         foreground="w")])
            txt = ax.text(i+1+0.15, row['min_tmpf']+0.5,
                          "%.0f" % (row['min_tmpf'],), fontsize=10,
                          ha='center', va='bottom', color='k')
            txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                         foreground="w")])
            i += 1
        ax.set_ylim(np.nanmin([df['low'].min(), df['min_tmpf'].min()]) - 5,
                    np.nanmax([df['high'].max(), df['max_tmpf'].max()]) + 5)
    ax.set_xlim(0.5, days + 0.5)
    ax.set_xticks(range(1, days+1))
    ax.set_xticklabels(np.arange(1, days+1), fontsize=8)
    ax.set_xlabel(sts.strftime("%B %Y"))
    ax.set_ylabel(r"Temperature $^\circ$F")

    if nt.sts[station]['ncdc81'] is None:
        subtitle = "Daily climatology unavailable for site"
    else:
        subtitle = ("NCDC 1981-2010 Climate Site: %s"
                    ) % (nt.sts[station]['ncdc81'],)

    ax.text(0, 1.01, ("[%s] %s :: Hi/Lo Temps for %s\n%s"
                      ) % (station, nt.sts[station]['name'],
                           sts.strftime("%b %Y"), subtitle),
            transform=ax.transAxes, ha='left', va='bottom')

    ax.yaxis.grid(linestyle='-')

    return fig, df


if __name__ == '__main__':
    plotter({'month': 4, 'year': 2016, 'station': 'RAYQ1',
             'network': 'CA_AB_DCP'})
