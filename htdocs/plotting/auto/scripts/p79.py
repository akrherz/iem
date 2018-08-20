"""Average dew point by wind direction"""
import datetime
from collections import OrderedDict

import psycopg2.extras
import numpy as np
import pandas as pd
from pyiem.plot.use_agg import plt
from pyiem.network import Table as NetworkTable
from pyiem.meteorology import mixing_ratio, dewpoint_from_pq
from pyiem.datatypes import temperature, pressure, mixingratio
from pyiem.util import get_autoplot_context, get_dbconn

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
    desc = dict()
    desc['data'] = True
    desc['cache'] = 86400
    desc['description'] = """This plot displays the average dew point at
    a given wind direction.  The average dew point is computed by taking the
    observations of mixing ratio, averaging those, and then back computing
    the dew point temperature.  With that averaged dew point temperature a
    relative humidity value is computed."""
    desc['arguments'] = [
        dict(type='zstation', name='zstation', default='DSM',
             label='Select Station:', network='IA_ASOS'),
        dict(type='select', name='month', default='all',
             label='Month Limiter', options=MDICT),

    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('asos')
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
        SELECT drct::int as t, dwpf from alldata where station = %s
        and drct is not null and dwpf is not null and dwpf <= tmpf
        and sknt > 3 and drct::int %% 10 = 0
        and extract(month from valid) in %s
        """, (station,  tuple(months)))
    sums = np.zeros((361,), 'f')
    counts = np.zeros((361,), 'f')
    for row in cursor:
        r = mixing_ratio(temperature(row[1], 'F')).value('KG/KG')
        sums[row[0]] += r
        counts[row[0]] += 1

    sums[0] = sums[360]
    counts[0] = counts[360]

    rows = []
    for i in range(361):
        if counts[i] < 3:
            continue
        r = sums[i] / float(counts[i])
        d = dewpoint_from_pq(pressure(1000, 'MB'),
                             mixingratio(r, 'KG/KG')
                             ).value('F')
        rows.append(dict(drct=i, dwpf=d))

    df = pd.DataFrame(rows)
    drct = df['drct']
    dwpf = df['dwpf']

    (fig, ax) = plt.subplots(1, 1)
    ax.bar(drct, dwpf, ec='green', fc='green', width=10, align='center')
    ax.grid(True, zorder=11)
    ax.set_title(("%s [%s]\nAverage Dew Point by Wind Direction (month=%s) "
                  "(%s-%s)\n"
                  "(must have 3+ hourly obs > 3 knots at given direction)"
                  ) % (nt.sts[station]['name'], station, month.upper(),
                       max([1973, nt.sts[station]['archive_begin'].year]),
                       datetime.datetime.now().year), size=10)

    ax.set_ylabel("Dew Point [F]")
    ax.set_ylim(min(dwpf)-5, max(dwpf)+5)
    ax.set_xlim(-5, 365)
    ax.set_xticks([0, 45, 90, 135, 180, 225, 270, 315, 360])
    ax.set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N'])
    ax.set_xlabel("Wind Direction")

    return fig, df


if __name__ == '__main__':
    plotter(dict())
