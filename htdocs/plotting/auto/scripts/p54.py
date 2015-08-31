import psycopg2.extras
import numpy as np
import datetime
import calendar
import pandas as pd
from pyiem.network import Table as NetworkTable


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['cache'] = 86400
    d['description'] = """This application plots the difference in morning
    low temperature between two sites of your choice.  The morning is
    defined as the period between midnight and 8 AM local time."""
    d['arguments'] = [
        dict(type='zstation', name='zstation1', default='ALO',
             network='IA_ASOS', label='Select Station 1:'),
        dict(type='zstation', name='zstation2', default='OLZ',
             network='AWOS', label='Select Station 2:'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
    cursor = ASOS.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station1 = fdict.get('zstation1', 'ALO')
    network1 = fdict.get('network1', 'IA_ASOS')
    station2 = fdict.get('zstation2', 'OLZ')
    network2 = fdict.get('network2', 'AWOS')

    nt1 = NetworkTable(network1)
    nt2 = NetworkTable(network2)

    cursor.execute("""
    WITH one as (
      SELECT date(valid), min(tmpf::int), avg(sknt)
      from alldata where station = %s
      and extract(hour from valid at time zone %s) between 0 and 8
      and tmpf is not null and tmpf between -70 and 140  GROUP by date),

    two as (
      SELECT date(valid), min(tmpf::int), avg(sknt)
      from alldata where station = %s
      and extract(hour from valid at time zone %s) between 0 and 8
      and tmpf is not null and tmpf between -70 and 140 GROUP by date)

    SELECT one.date, one.min- two.min, one.avg, two.avg from
    one JOIN two on (one.date = two.date) WHERE one.avg >= 0
    and one.min - two.min between -25 and 25
    """, (station1, nt1.sts[station1]['tzname'],
          station2, nt2.sts[station2]['tzname']))

    weeks = []
    deltas = []
    days = []
    sknts = []
    for row in cursor:
        days.append(row[0])
        weeks.append(int(row[0].strftime("%W")))
        deltas.append(row[1])
        sknts.append(row[2])
    df = pd.DataFrame(dict(day=pd.Series(days),
                           week=pd.Series(weeks),
                           delta=pd.Series(deltas),
                           sknt=pd.Series(sknts)))

    sts = datetime.datetime(2012, 1, 1)
    xticks = []
    for i in range(1, 13):
        ts = sts.replace(month=i)
        xticks.append(int(ts.strftime("%j")))

    (fig, ax) = plt.subplots(2, 1)

    ax[0].set_title(("[%s] %s minus [%s] %s\n"
                     "Mid-7AM Low Temp Difference Period: %s - %s"
                     ) % (station1, nt1.sts[station1]['name'],
                          station2, nt2.sts[station2]['name'],
                          min(days), max(days)))

    bins = np.arange(-20.5, 20.5, 1)
    H, xedges, yedges = np.histogram2d(weeks, deltas, [range(0, 54), bins])
    H = np.ma.array(H)
    H.mask = np.where(H < 1, True, False)
    ax[0].pcolormesh((xedges - 1) * 7, yedges, H.transpose(),
                     cmap=cm.get_cmap("Greens"))
    ax[0].set_xticks(xticks)
    ax[0].set_xticklabels(calendar.month_abbr[1:])
    ax[0].set_xlim(0, 366)

    y = []
    for i in range(np.shape(H)[0]):
        y.append(np.ma.sum(H[i, :] * (bins[:-1]+0.5)) / np.ma.sum(H[i, :]))

    ax[0].plot(xedges[:-1]*7, y, zorder=3, lw=3, color='k')
    ax[0].plot(xedges[:-1]*7, y, zorder=3, lw=1, color='w')

    rng = min([max([max(deltas), 0-min(deltas)]), 12])
    ax[0].set_ylim(0-rng-2, rng+2)
    ax[0].grid(True)
    ax[0].set_ylabel("Low Temp Diff $^\circ$F")
    ax[0].text(-0.01, 1.02, "%s\nWarmer" % (station1,),
               transform=ax[0].transAxes, va='top', ha='right', fontsize=8)
    ax[0].text(-0.01, -0.02, "%s\nColder" % (station1,),
               transform=ax[0].transAxes, va='bottom', ha='right', fontsize=8)

    H, xedges, yedges = np.histogram2d(sknts, deltas, [range(0, 31), bins])
    H = np.ma.array(H)
    H.mask = np.where(H < 1, True, False)
    ax[1].pcolormesh((xedges - 0.5), yedges, H.transpose(),
                     cmap=cm.get_cmap('Greens'))

    y = []
    for i in range(np.shape(H)[0]):
        y.append(np.ma.sum(H[i, :] * (bins[:-1]+0.5)) / np.ma.sum(H[i, :]))

    ax[1].plot(xedges[:-1], y, zorder=3, lw=3, color='k')
    ax[1].plot(xedges[:-1], y, zorder=3, lw=1, color='w')

    ax[1].set_ylim(0-rng-2, rng+2)
    ax[1].grid(True)
    ax[1].set_xlim(left=-0.25)
    ax[1].set_xlabel("Average Wind Speed [kts] for %s" % (station1,))
    ax[1].set_ylabel("Low Temp Diff $^\circ$F")
    ax[1].text(-0.01, 1.02,
               "%s\nWarmer" % (station1,), transform=ax[1].transAxes,
               va='top', ha='right', fontsize=8)
    ax[1].text(-0.01, -0.02,
               "%s\nColder" % (station1,), transform=ax[1].transAxes,
               va='bottom', ha='right', fontsize=8)

    return fig, df
