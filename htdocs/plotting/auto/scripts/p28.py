import psycopg2.extras
import numpy as np
import datetime
import pandas as pd
from pyiem.network import Table as NetworkTable


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    today = datetime.date.today()
    d['data'] = True
    d['description'] = """This plot presents three metrics for to date
    precipitation accumulation over a given number of trailing days.  The
    lines represent the actual and maximum accumulations for the period.
    The blue bars represent the rank with 1 being the wettest on record."""
    d['arguments'] = [
        dict(type='station', name='station', default='IA0200',
             label='Select Station:'),
        dict(type='date', name='date', default=today.strftime("%Y/%m/%d"),
             label='To Date:',
             min="1894/01/01"),  # Comes back to python as yyyy-mm-dd

    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0200')
    date = datetime.datetime.strptime(fdict.get('date', '2014-10-15'),
                                      '%Y-%m-%d')

    table = "alldata_%s" % (station[:2],)
    nt = NetworkTable("%sCLIMATE" % (station[:2],))

    cursor.execute("""
    SELECT year,  extract(doy from day) as doy, precip
    from """+table+""" where station = %s and precip is not null
    """, (station,))

    baseyear = nt.sts[station]['archive_begin'].year - 1
    years = (datetime.datetime.now().year - baseyear) + 1

    data = np.zeros((years, 367*2))
    # 1892 1893
    # 1893 1894
    # 1894 1895

    for row in cursor:
        # left hand
        data[int(row['year'] - baseyear), int(row['doy'])] = row['precip']
        # right hand
        data[int(row['year'] - baseyear - 1),
             int(row['doy']) + 366] = row['precip']

    _temp = date.replace(year=2000)
    _doy = int(_temp.strftime("%j"))
    xticks = []
    xticklabels = []
    for i in range(-366, 0):
        ts = _temp + datetime.timedelta(days=i)
        if ts.day == 1:
            xticks.append(i)
            xticklabels.append(ts.strftime("%b"))
    ranks = []
    totals = []
    maxes = []
    myyear = date.year - baseyear - 1
    for days in range(1, 366):
        idx0 = _doy + 366 - days
        idx1 = _doy + 366
        sums = np.sum(data[:, idx0:idx1], 1)
        thisyear = sums[myyear]
        sums = np.sort(sums)
        a = np.digitize([thisyear, ], sums)
        rank = years - a[0] + 1
        ranks.append(rank)
        totals.append(thisyear)
        maxes.append(sums[-1])

    (fig, ax) = plt.subplots(1, 1)
    ax.bar(np.arange(-365, 0), ranks[::-1], fc='b', ec='b')
    ax.grid(True)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.set_title(("%s %s\nTrailing Days Precipitation Rank [%s-%s] to %s"
                  ) % (station, nt.sts[station]['name'], baseyear+2,
                       datetime.datetime.now().year,
                       date.strftime("%-d %b %Y")))
    ax.set_ylabel("Rank [1=wettest] (bars)")
    ax.set_xlim(-367, 0.5)

    y2 = ax.twinx()
    y2.plot(np.arange(-365, 0), totals[::-1], color='r', lw=2,
            label='This Period')
    y2.plot(np.arange(-365, 0), maxes[::-1], color='g', lw=2,
            label='Maximum')
    y2.set_ylabel("Precipitation [inch]")

    y2.legend()
    df = pd.DataFrame(dict(day=np.arange(-365, 0),
                           maxaccum=maxes[::-1],
                           accum=totals[::-1],
                           rank=ranks[::-1]))

    return fig, df
