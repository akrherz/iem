import psycopg2.extras
import numpy as np
import datetime
import pytz
from pyiem.network import Table as NetworkTable


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['cache'] = 86400
    d['description'] = """This chart is an attempted illustration of the amount
    of cloudiness that existed at a METAR site for a given month.  The chart
    combines reports of cloud amount and level to provide a visual
    representation of the cloudiness.  Once the METAR site hits a cloud level
    of overcast, it can no longer sense clouds above that level.  So while the
    chart will indicate cloudiness up to the top, it may not have been like
    that in reality.
    """
    today = datetime.date.today()
    d['arguments'] = [
        dict(type='zstation', name='zstation', default='DSM',
             label='Select Station:'),
        dict(type='month', name='month', label='Select Month:',
             default=today.month),
        dict(type='year', name='year', label='Select Year:',
             default=today.year, min=1970),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
    acursor = ASOS.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('zstation', 'AMW')
    network = fdict.get('network', 'IA_ASOS')
    year = int(fdict.get('year', 2014))
    month = int(fdict.get('month', 12))

    nt = NetworkTable(network)

    # Extract the range of forecasts for each day for approximately
    # the given month
    sts = datetime.datetime(year, month, 1, 0, 0)
    sts = sts.replace(tzinfo=pytz.timezone("UTC"))
    ets = (sts + datetime.timedelta(days=35)).replace(day=1)
    days = (ets-sts).days
    data = np.zeros((250, days * 24))

    acursor.execute("""
    SELECT valid, skyc1, skyc2, skyc3, skyc4, skyl1, skyl2, skyl3, skyl4
    from alldata where station = %s and valid BETWEEN %s and %s
    ORDER by valid ASC
    """, (station, sts, ets))

    lookup = {'CLR': 0, 'FEW': 25, 'SCT': 50, 'BKN': 75, 'OVC': 100}

    if acursor.rowcount == 0:
        return "No database entries found for station, sorry!"

    for row in acursor:
        delta = (row[0] - sts).days * 24.0 + (row[0] - sts).seconds / 3600.
        for i in range(1, 5):
            a = lookup.get(row[i], 0)
            if a > 0:
                l = row[i+4]
                if l is not None and l > 0:
                    l = l / 100
                    if l >= 250:
                        continue
                    data[l:l+4, int(delta)] = a
                    data[l+3:, int(delta)] = min(a, 75)

    data[:, delta:] = 15

    data = np.ma.array(data, mask=np.where(data == 0, True, False))

    (fig, ax) = plt.subplots(1, 1)

    ax.set_axis_bgcolor('skyblue')
    ax.set_xticks(np.arange(0, days*24+1, 24))
    ax.set_xticklabels(np.arange(1, days+1))

    ax.set_title(('[%s] %s %s Clouds\nbased on ASOS METAR Cloud Amount '
                  'and Level Reports'
                  ) % (station, nt.sts[station]['name'],
                       sts.strftime("%b %Y")))

    ax.imshow(np.flipud(data), aspect='auto', extent=[0, days*24, 0, 250],
              cmap=cm.get_cmap('gray_r'))
    ax.set_yticks(range(0, 260, 50))
    ax.set_yticklabels(range(0, 25, 5))
    ax.set_ylabel("Cloud Levels [1000s feet]")
    ax.set_xlabel("Day of %s (UTC Timezone)" % (sts.strftime("%b %Y"),))

    from matplotlib.patches import Rectangle
    r = Rectangle((0, 0), 1, 1, fc='skyblue')
    r2 = Rectangle((0, 0), 1, 1, fc='white')
    r3 = Rectangle((0, 0), 1, 1, fc='k')
    r4 = Rectangle((0, 0), 1, 1, fc='#EEEEEE')

    ax.grid(True)
    # Shrink current axis's height by 10% on the bottom
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1,
                     box.width, box.height * 0.9])

    ax.legend([r, r4, r2, r3], ['Clear', 'Some', 'Unknown',
                                'Obscured by Overcast'],
              loc='upper center',
              bbox_to_anchor=(0.5, -0.08), fancybox=True, shadow=True, ncol=4)

    return fig
