import psycopg2.extras
import datetime
import numpy as np
from pyiem.network import Table as NetworkTable
from pyiem.meteorology import mixing_ratio, dewpoint_from_pq, relh
from pyiem.datatypes import temperature, pressure, mixingratio
import pandas as pd
from collections import OrderedDict
from pyiem.util import get_autoplot_context

MDICT = OrderedDict([
         ('all', 'No Month/Time Limit'),
         ('spring', 'Spring (MAM)'),
         ('fall', 'Fall (SON)'),
         ('winter', 'Winter (DJF)'),
         ('summer', 'Summer (JJA)'),
         ('jan', 'January'),
         ('feb', 'February'),
         ('mar', 'March'),
         ('apr', 'April'),
         ('may', 'May'),
         ('jun', 'June'),
         ('jul', 'July'),
         ('aug', 'August'),
         ('sep', 'September'),
         ('oct', 'October'),
         ('nov', 'November'),
         ('dec', 'December')])


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['cache'] = 86400
    d['description'] = """This plot displays the average dew point at
    a given air temperature.  The average dew point is computed by taking the
    observations of mixing ratio, averaging those, and then back computing
    the dew point temperature.  With that averaged dew point temperature a
    relative humidity value is computed."""
    d['arguments'] = [
        dict(type='zstation', name='zstation', default='DSM',
             label='Select Station:', network='IA_ASOS'),
        dict(type='select', name='month', default='all',
             label='Month Limiter', options=MDICT),

    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='asos', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['zstation']
    network = ctx['network']
    month = ctx['month']

    nt = NetworkTable(network)

    if month == 'all':
        months = range(1, 13)
    elif month == 'fall':
        months = [9, 10, 11]
    elif month == 'winter':
        months = [12, 1, 2]
    elif month == 'spring':
        months = [3, 4, 5]
    elif month == 'summer':
        months = [6, 7, 8]
    else:
        ts = datetime.datetime.strptime("2000-"+month+"-01", '%Y-%b-%d')
        # make sure it is length two for the trick below in SQL
        months = [ts.month, 999]

    cursor.execute("""
        SELECT tmpf::int as t, dwpf from alldata where station = %s
        and tmpf is not null and dwpf is not null and dwpf <= tmpf
        and tmpf >= 0 and tmpf <= 140
        and extract(month from valid) in %s
        """, (station,  tuple(months)))
    sums = np.zeros((140,), 'f')
    counts = np.zeros((140,), 'f')
    for row in cursor:
        r = mixing_ratio(temperature(row[1], 'F')).value('KG/KG')
        sums[row[0]] += r
        counts[row[0]] += 1

    rows = []
    for i in range(140):
        if counts[i] < 3:
            continue
        r = sums[i] / float(counts[i])
        d = dewpoint_from_pq(pressure(1000, 'MB'),
                             mixingratio(r, 'KG/KG')
                             ).value('F')
        rh = relh(temperature(i, 'F'), temperature(d, 'F')).value('%')
        rows.append(dict(tmpf=i, dwpf=d, rh=rh))

    df = pd.DataFrame(rows)
    tmpf = df['tmpf']
    dwpf = df['dwpf']
    rh = df['rh']

    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))
    ax.bar(tmpf-0.5, dwpf, ec='green', fc='green', width=1)
    ax.grid(True, zorder=11)
    ax.set_title(("%s [%s]\nAverage Dew Point by Air Temperature (month=%s) "
                  "(%s-%s)\n"
                  "(must have 3+ hourly observations at the given temperature)"
                  ) % (nt.sts[station]['name'], station, month.upper(),
                       nt.sts[station]['archive_begin'].year,
                       datetime.datetime.now().year), size=10)

    ax.plot([0, 140], [0, 140], color='b')
    ax.set_ylabel("Dew Point [F]")
    y2 = ax.twinx()
    y2.plot(tmpf, rh, color='k')
    y2.set_ylabel("Relative Humidity [%] (black line)")
    y2.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    y2.set_ylim(0, 100)
    ax.set_ylim(0, max(tmpf)+2)
    ax.set_xlim(0, max(tmpf)+2)
    ax.set_xlabel("Air Temperature $^\circ$F")

    return fig, df

if __name__ == '__main__':
    plotter(dict())
