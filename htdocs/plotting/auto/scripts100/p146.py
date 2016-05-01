import psycopg2
from pyiem.network import Table as NetworkTable
import datetime
import calendar
import numpy as np
from pandas.io.sql import read_sql
import pandas as pd


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This chart displays the frequency of having
    measurable precipitation reported by an ASOS site and the air temperature
    that was reported at the same time.  This chart makes an assumption
    about the two values being coincident, whereas in actuality they may not
    have been.
    """
    d['arguments'] = [
        dict(type='zstation', name='zstation', default='AMW',
             label='Select Station:'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='asos', host='iemdb', user='nobody')

    station = fdict.get('zstation', 'AMW')
    network = fdict.get('network', 'IA_ASOS')
    nt = NetworkTable(network)

    df = read_sql("""
    WITH obs as (
        SELECT date_trunc('hour', valid) as t, avg(tmpf) as avgt from alldata
        WHERE station = %s and p01i >= 0.01 and tmpf is not null
        GROUP by t
    )

    SELECT extract(week from t) as week, avgt from obs
    """, pgconn, params=(station,), index_col=None)

    sts = datetime.datetime(2012, 1, 1)
    xticks = []
    for i in range(1, 13):
        ts = sts.replace(month=i)
        xticks.append(int(ts.strftime("%j")))

    (fig, ax) = plt.subplots(1, 1)

    bins = np.arange(df['avgt'].min() - 5, df['avgt'].max() + 5, 2)
    H, xedges, yedges = np.histogram2d(df['week'].values,
                                       df['avgt'].values, [range(0, 54), bins])
    rows = []
    for i, x in enumerate(xedges[:-1]):
        for j, y in enumerate(yedges[:-1]):
            rows.append(dict(tmpf=y, week=x, count=H[i, j]))
    resdf = pd.DataFrame(rows)

    years = datetime.date.today().year - nt.sts[station]['archive_begin'].year
    H = np.ma.array(H) / float(years)
    H.mask = np.ma.where(H < 0.1, True, False)
    res = ax.pcolormesh((xedges - 1) * 7, yedges, H.transpose(),
                        cmap=plt.get_cmap("jet"))
    fig.colorbar(res, label='Hours per week per year')
    ax.set_xticks(xticks)
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(0, 366)

    y = []
    for i in range(np.shape(H)[0]):
        y.append(np.ma.sum(H[i, :] * (bins[:-1]+0.5)) / np.ma.sum(H[i, :]))

    ax.plot(xedges[:-1]*7, y, zorder=3, lw=3, color='w')
    ax.plot(xedges[:-1]*7, y, zorder=3, lw=1, color='k', label='Average')
    ax.legend(loc=2)

    ax.set_title(("[%s] %s (%s-%s)\n"
                  "Temperature Frequency During Precipitation by Week"
                  ) % (station, nt.sts[station]['name'],
                       nt.sts[station]['archive_begin'].year,
                       datetime.date.today().year))
    ax.grid(True)
    ax.set_ylabel("Temperature [$^\circ$F]")

    return fig, resdf
