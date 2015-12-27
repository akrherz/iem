import numpy as np
import datetime
import psycopg2
from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
import warnings
warnings.simplefilter("ignore", UserWarning)


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['cache'] = 300
    today = datetime.date.today()
    mo = today.month
    yr = today.year
    d['data'] = True
    d['description'] = """Daily plot of observed high and low temperatures
    along with the daily climatology for the nearest (sometimes same) location.
    """
    d['arguments'] = [
        dict(type='zstation', name='station', default='AMW',
             label='Select Station:'),
        dict(type="month", name="month", default=mo, label="Select Month"),
        dict(type="year", name="year", default=yr, label="Select Year",
             minvalue=2000),
    ]
    return d


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

    station = fdict.get('station', 'AMW')
    network = fdict.get('network', 'IA_ASOS')
    year = int(fdict.get('year', 2014))
    month = int(fdict.get('month', 8))
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
    SELECT to_char(day, 'mmdd') as sday, day, max_tmpf, min_tmpf
    from """+table+""" s JOIN stations t
    on (t.iemid = s.iemid) WHERE id = %s and network = %s and
    day >= %s and day < %s ORDER by day ASC
    """, pgconn_iem,  params=(station, network, sts, ets), index_col='sday')
    has_data = (len(df.index) > 0)

    # Get the normals
    cdf = read_sql("""
    SELECT to_char(valid, 'mmdd') as sday, valid, high, low from
    ncdc_climate81 where station = %s
    and extract(month from valid) = %s ORDER by valid ASC
    """, pgconn_coop, params=(nt.sts[station]['ncdc81'], month),
                   index_col='sday')

    df = cdf.join(df)

    (fig, ax) = plt.subplots(1, 1)

    for day in weekends:
        rect = Rectangle([day-0.5, -100], 1, 300, facecolor='#EEEEEE',
                         edgecolor='None')
        ax.add_patch(rect)

    ax.plot(np.arange(1, days+1), df['high'].values, zorder=3, marker='o',
            color='pink')
    ax.plot(np.arange(1, days+1), df['low'].values, zorder=3, marker='o',
            color='skyblue')
    if has_data:
        ax.bar(np.arange(1, days+1) - 0.3, df['max_tmpf'].values,
               fc='r', ec='k', width=0.3,
               linewidth=0.6)
        ax.bar(np.arange(1, days+1), df['min_tmpf'].values,
               fc='b', ec='k', width=0.3,
               linewidth=0.6)
    else:
        ax.text(0.5, 0.5, "No Data Found", transform=ax.transAxes)
        ax.set_ylim(0, 1)

    i = 0
    for _, row in df.iterrows():
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
    ax.set_ylim(min(df['low'].min(), df['min_tmpf'].min()) - 5,
                max(df['high'].max(), df['max_tmpf'].max()) + 5)
    ax.set_xlim(0.5, days + 0.5)
    ax.set_xticks(np.arange(1, days+1))
    ax.set_xticklabels(np.arange(1, days+1), fontsize=8)
    ax.set_xlabel(sts.strftime("%B %Y"))
    ax.set_ylabel("Temperature $^\circ$F")

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
