import psycopg2.extras
import numpy as np
import datetime
import pandas as pd
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
    IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
    cursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)

    COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)

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

    highs = [-99]*days
    lows = [99]*days

    cursor.execute("""
    SELECT day, coalesce(max_tmpf, -99), coalesce(min_tmpf, 99)
    from """+table+""" s JOIN stations t
    on (t.iemid = s.iemid) WHERE id = %s and network = %s and
    day >= %s and day < %s
    """, (station, network, sts, ets))

    has_data = False
    rows = []
    for row in cursor:
        has_data = True
        rows.append(dict(day=row[0].day, high=row[1], low=row[2],
                         climate_high=None, climate_low=None))
        highs[int(row[0].day) - 1] = row[1]
        lows[int(row[0].day) - 1] = row[2]
    df = pd.DataFrame(rows)
    highs = np.ma.array(highs)
    highs.mask = np.ma.where(highs < -98, True, False)
    lows = np.ma.array(lows)
    lows.mask = np.ma.where(lows > 98, True, False)

    # Get the normals
    ccursor.execute("""
    SELECT valid, high, low from ncdc_climate81 where station = %s
    and extract(month from valid) = %s
    """, (nt.sts[station]['ncdc81'], month))

    clhighs = [None]*days
    cllows = [None]*days
    for row in ccursor:
        idx = int(row[0].day) - 1
        # February leap day
        if idx >= days:
            continue
        clhighs[idx] = row[1]
        cllows[idx] = row[2]

    (fig, ax) = plt.subplots(1, 1)

    for day in weekends:
        rect = Rectangle([day-0.5, -100], 1, 300, facecolor='#EEEEEE',
                         edgecolor='None')
        ax.add_patch(rect)

    ax.plot(np.arange(1, days+1), clhighs, zorder=3, marker='o',
            color='pink')
    ax.plot(np.arange(1, days+1), cllows, zorder=3, marker='o',
            color='skyblue')
    if has_data:
        ax.bar(np.arange(1, days+1) - 0.3, highs, fc='r', ec='k', width=0.3,
               linewidth=0.6)
        ax.bar(np.arange(1, days+1), lows, fc='b', ec='k', width=0.3,
               linewidth=0.6)
    else:
        ax.text(0.5, 0.5, "No Data Found", transform=ax.transAxes)
        ax.set_ylim(0, 1)

    for i in range(days):
        txt = ax.text(i+1-0.15, highs[i]+0.5, "%.0f" % (highs[i],),
                      fontsize=10, ha='center', va='bottom', color='k')
        txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                     foreground="w")])
        txt = ax.text(i+1+0.15, lows[i]+0.5,
                      "%.0f" % (lows[i],), fontsize=10,
                      ha='center', va='bottom', color='k')
        txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                     foreground="w")])
    if ccursor.rowcount > 0:
        ax.set_ylim(min(min(cllows), min(lows))-5,
                    max(max(clhighs), max(highs))+5)
    else:
        if has_data:
            ax.set_ylim(min(lows)-5, max(highs)+5)
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
