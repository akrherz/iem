"""Hourly temp impacts from clouds"""
import datetime

import psycopg2.extras
import numpy as np
import pandas as pd
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.network import Table as NetworkTable


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['desciption'] = """This plot attempts to show the impact of cloudiness
    on temperatures.  The plot shows a simple difference between the average
    temperature during cloudy/mostly cloudy conditions and the average
    temperature by hour and by week of the year."""
    desc['arguments'] = [
        dict(type='zstation', name='zstation', default='DSM',
             label='Select Station:', network='IA_ASOS'),
    ]
    return desc


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = get_dbconn('asos')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['zstation']
    network = ctx['network']
    nt = NetworkTable(network)

    data = np.zeros((24, 52), 'f')

    cursor.execute("""
    WITH data as (
     SELECT valid at time zone %s + '10 minutes'::interval as v,
     tmpf, skyc1, skyc2, skyc3 from alldata WHERE station = %s
     and tmpf is not null and tmpf > -99 and tmpf < 150),


    climo as (
     select extract(week from v) as w,
     extract(hour from v) as hr,
     avg(tmpf) from data GROUP by w, hr),

    cloudy as (
     select extract(week from v) as w,
     extract(hour from v) as hr,
     avg(tmpf) from data WHERE (skyc1 in ('BKN','OVC') or
     skyc2 in ('BKN','OVC') or skyc3 in ('BKN','OVC')) GROUP by w, hr)

    SELECT l.w, l.hr, l.avg - c.avg from cloudy l JOIN climo c on
    (l.w = c.w and l.hr = c.hr)
    """, (nt.sts[station]['tzname'], station))

    for row in cursor:
        if row[0] > 52:
            continue
        data[int(row[1]), int(row[0]) - 1] = row[2]
    rows = []
    for week in range(52):
        for hour in range(24):
            rows.append(dict(hour=hour, week=(week+1), count=data[hour, week]))
    df = pd.DataFrame(rows)

    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))

    maxv = np.ceil(max([np.max(data), 0 - np.min(data)])) + 0.2
    cs = ax.imshow(data, aspect='auto', interpolation='nearest',
                   vmin=(0 - maxv), vmax=maxv, cmap=plt.get_cmap('RdYlGn_r'))
    a = fig.colorbar(cs)
    a.ax.set_ylabel('Temperature Departure $^{\circ}\mathrm{F}$')
    ax.grid(True)
    ax.set_title(("[%s] %s %s-%s\nHourly Temp Departure "
                  "(skies were mostly cloudy vs all)"
                  ) % (station, nt.sts[station]['name'],
                       nt.sts[station]['archive_begin'].year,
                       datetime.date.today().year))
    ax.set_ylim(-0.5, 23.5)
    ax.set_ylabel("Local Hour of Day, %s" % (nt.sts[station]['tzname'],))
    ax.set_yticks((0, 4, 8, 12, 16, 20))
    ax.set_xticks(range(0, 55, 7))
    ax.set_xticklabels(('Jan 1', 'Feb 19', 'Apr 8', 'May 27', 'Jul 15',
                        'Sep 2', 'Oct 21', 'Dec 9'))

    ax.set_yticklabels(('Mid', '4 AM', '8 AM', 'Noon', '4 PM', '8 PM'))

    return fig, df


if __name__ == '__main__':
    plotter(dict())
