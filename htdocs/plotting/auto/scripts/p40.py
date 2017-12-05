"""METAR cloudiness"""
import datetime

import numpy as np
from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
from pyiem.util import get_autoplot_context, get_dbconn, utc


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['cache'] = 3600
    desc['description'] = """This chart is an attempted illustration of the amount
    of cloudiness that existed at a METAR site for a given month.  The chart
    combines reports of cloud amount and level to provide a visual
    representation of the cloudiness.  Once the METAR site hits a cloud level
    of overcast, it can no longer sense clouds above that level.  So while the
    chart will indicate cloudiness up to the top, it may not have been like
    that in reality.
    """
    today = datetime.date.today()
    desc['arguments'] = [
        dict(type='zstation', name='zstation', default='DSM',
             network='IA_ASOS', label='Select Station:'),
        dict(type='month', name='month', label='Select Month:',
             default=today.month),
        dict(type='year', name='year', label='Select Year:',
             default=today.year, min=1970),
    ]
    return desc


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    from matplotlib.patches import Rectangle
    pgconn = get_dbconn('asos')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['zstation']
    network = ctx['network']
    year = ctx['year']
    month = ctx['month']

    nt = NetworkTable(network)

    # Extract the range of forecasts for each day for approximately
    # the given month
    sts = utc(year, month, 1, 0, 0)
    ets = (sts + datetime.timedelta(days=35)).replace(day=1)
    days = (ets-sts).days
    data = np.ones((250, days * 24)) * -1

    df = read_sql("""
    SELECT valid, skyc1, skyc2, skyc3, skyc4, skyl1, skyl2, skyl3, skyl4
    from alldata where station = %s and valid BETWEEN %s and %s
    and report_type = 2
    ORDER by valid ASC
    """, pgconn, params=(station, sts, ets), index_col=None)

    lookup = {'CLR': 0, 'FEW': 25, 'SCT': 50, 'BKN': 75, 'OVC': 100}

    if df.empty:
        return "No database entries found for station, sorry!"

    for _, row in df.iterrows():
        delta = int((row['valid'] - sts).total_seconds() / 3600 - 1)
        data[:, delta] = 0
        for i in range(1, 5):
            a = lookup.get(row['skyc%s' % (i,)], -1)
            if a >= 0:
                skyl = row['skyl%s' % (i,)]
                if skyl is not None and skyl > 0:
                    skyl = int(skyl / 100)
                    if skyl >= 250:
                        continue
                    data[skyl:skyl+4, delta] = a
                    data[skyl+3:, delta] = min(a, 75)

    data = np.ma.array(data, mask=np.where(data < 0, True, False))

    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))

    ax.set_facecolor('skyblue')
    ax.set_xticks(np.arange(0, days*24+1, 24))
    ax.set_xticklabels(np.arange(1, days+1))

    ax.set_title(('[%s] %s %s Clouds\nbased on ASOS METAR Cloud Amount '
                  'and Level Reports'
                  ) % (station, nt.sts[station]['name'],
                       sts.strftime("%b %Y")))

    cmap = cm.get_cmap('gray_r')
    cmap.set_bad('white')
    cmap.set_under('skyblue')
    ax.imshow(np.flipud(data), aspect='auto', extent=[0, days*24, 0, 250],
              cmap=cmap, vmin=1)
    ax.set_yticks(range(0, 260, 50))
    ax.set_yticklabels(range(0, 25, 5))
    ax.set_ylabel("Cloud Levels [1000s feet]")
    ax.set_xlabel("Day of %s (UTC Timezone)" % (sts.strftime("%b %Y"),))

    r1 = Rectangle((0, 0), 1, 1, fc='skyblue')
    r2 = Rectangle((0, 0), 1, 1, fc='white')
    r3 = Rectangle((0, 0), 1, 1, fc='k')
    r4 = Rectangle((0, 0), 1, 1, fc='#EEEEEE')

    ax.grid(True)
    # Shrink current axis's height by 10% on the bottom
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1,
                     box.width, box.height * 0.9])

    ax.legend([r1, r4, r2, r3], ['Clear', 'Some', 'Unknown',
                                 'Obscured by Overcast'],
              loc='upper center', fontsize=14,
              bbox_to_anchor=(0.5, -0.09), fancybox=True, shadow=True, ncol=4)

    return fig, df


if __name__ == '__main__':
    plotter(dict(station='DSM', year=2016, month=9, network='IA_ASOS'))
