import psycopg2.extras
from pyiem.network import Table as NetworkTable
import numpy as np
import pandas as pd
import datetime
import pytz
from pyiem.util import get_autoplot_context


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This plot looks at the bias associated with computing
    24 hour precipitation totals using a given hour of the day as the
    delimiter. This plot will take a number of seconds to generate, so please
    be patient.  This chart attempts to address the question of if computing
    24 hour precip totals at midnight or 7 AM biases the totals.  Such biases
    are commmon when computing this metric for high or low temperature."""
    d['arguments'] = [
        dict(type='zstation', name='zstation', default='DSM',
             label='Select Station:', network='IA_ASOS'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='iem', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())

    station = ctx['zstation']
    network = ctx['network']
    nt = NetworkTable(network)

    jan1 = datetime.datetime.now().replace(hour=0, day=1, month=1, minute=0,
                                           second=0, microsecond=0,
                                           tzinfo=pytz.timezone("UTC"))
    ts1973 = datetime.datetime(1973, 1, 1)
    today = datetime.datetime.now()
    cursor.execute("""
    SELECT valid at time zone 'UTC', phour from hourly WHERE
    station = %s and network = %s and phour >= 0.01 and
    valid >= '1973-01-01 00:00+00' and valid < %s
    """, (station, network, jan1))

    days = (jan1.year - 1973) * 366
    data = np.zeros((days * 24), 'f')
    minvalid = today
    for row in cursor:
        if row[0] < minvalid:
            minvalid = row[0]
        data[(row[0] - ts1973).days * 24 + row[0].hour] = row[1]

    lts = jan1.astimezone(pytz.timezone(nt.sts[station]['tzname']))
    lts = lts.replace(month=7, hour=0)
    cnts = [0]*24
    avgv = [0]*24
    rows = []
    for hr in range(24):
        ts = lts.replace(hour=hr)
        z = ts.astimezone(pytz.timezone("UTC")).hour
        a = np.reshape(data[z:(0 - 24 + z)], (days-1, 24))
        tots = np.sum(a, 1)
        cnts[hr] = np.sum(np.where(tots > 0, 1, 0))
        avgv[hr] = np.average(tots[tots > 0])
        rows.append(dict(average_precip=avgv[hr], events=cnts[hr],
                         zhour=z, localhour=hr))

    df = pd.DataFrame(rows)
    (fig, ax) = plt.subplots(1, 1)
    acount = np.average(cnts)
    years = today.year - minvalid.year
    arc = (np.array(cnts)-acount) / float(years)
    maxv = max([0 - np.min(arc), np.max(arc)])
    l = ax.plot(range(24), arc, color='b', label='Days Bias')
    ax.set_ylim(0 - maxv - 0.2, maxv + 0.2)

    ax2 = ax.twinx()
    aavg = np.average(avgv)
    aavgv = np.array(avgv) - aavg
    l2 = ax2.plot(range(24), aavgv, color='r')
    maxv = max([0 - np.min(aavgv), np.max(aavgv)])
    ax2.set_ylim(0 - maxv - 0.01, maxv + 0.01)
    ax2.set_ylabel("Bias with Average 24 Hour Precip [in/day]", color='r')
    ax.set_title(("[%s] %s %s-%s\n"
                  "Bias of 24 Hour 'Day' Split for Precipitation"
                  ) % (station, nt.sts[station]['name'],
                       minvalid.year,
                       datetime.date.today().year))
    ax.set_ylabel("Bias of Days per Year with Precip", color='b')
    ax.set_xlim(0, 24)
    ax.set_xticks((0, 4, 8, 12, 16, 20, 24))
    ax.set_xticklabels(('Mid', '4 AM', '8 AM', 'Noon', '4 PM', '8 PM', 'Mid'))
    ax.grid(True)
    ax.set_xlabel(("Hour Used for 24 Hour Summary, Timezone: %s"
                   ) % (nt.sts[station]['tzname'], ))
    box = ax.get_position()
    ax.set_position([box.x0, box.y0,
                     box.width * .95, box.height])
    ax2.set_position([box.x0, box.y0,
                     box.width * .95, box.height])
    ax.legend([l[0], l2[0]], ['Days Bias', 'Avg Precip Bias'], loc='best',
              fontsize=10)
    return fig, df
