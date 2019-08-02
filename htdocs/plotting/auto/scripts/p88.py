"""Hourly temp impacts from clouds"""
import datetime
from collections import OrderedDict

import numpy as np
from pandas.io.sql import read_sql
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.plot.use_agg import plt
from pyiem.exceptions import NoDataFound

PDICT = OrderedDict((
    ['clear', 'clear'],
    ['cloudy', 'mostly cloudy'],
))


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['desciption'] = """This plot attempts to show the impact of cloudiness
    on temperatures.  The plot shows a simple difference between the average
    temperature during cloudy/mostly cloudy conditions and the average
    temperature by hour and by week of the year.  The input data for this
    chart is limited to post 1973 as cloud cover data since then is more
    reliable/comparable."""
    desc['arguments'] = [
        dict(type='zstation', name='zstation', default='DSM',
             label='Select Station:', network='IA_ASOS'),
        dict(type='select', name='which', default='cloudy', options=PDICT,
             label='Compute differences based on:'),
        dict(
            type='cmap', name='cmap', default='RdYlGn_r', label='Color Ramp:'),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('asos')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['zstation']
    which = ctx['which']

    data = np.zeros((24, 52), 'f')

    sql = "in ('BKN','OVC')" if which == 'cloudy' else "= 'CLR'"
    df = read_sql("""
    WITH data as (
     SELECT valid at time zone %s + '10 minutes'::interval as v,
     tmpf, skyc1, skyc2, skyc3, skyc4 from alldata WHERE station = %s
     and valid > '1973-01-01'
     and tmpf is not null and tmpf > -99 and tmpf < 150),


    climo as (
     select extract(week from v) as w,
     extract(hour from v) as hr,
     avg(tmpf) from data GROUP by w, hr),

    cloudy as (
     select extract(week from v) as w,
     extract(hour from v) as hr,
     avg(tmpf) from data WHERE skyc1 """ + sql + """ or
     skyc2 """ + sql + """ or skyc3 """ + sql + """ or skyc4 """ + sql + """
     GROUP by w, hr)

    SELECT l.w as week, l.hr as hour, l.avg - c.avg as difference
    from cloudy l JOIN climo c on
    (l.w = c.w and l.hr = c.hr)
    """, pgconn, params=(ctx['_nt'].sts[station]['tzname'], station))

    for _, row in df.iterrows():
        if row[0] > 52:
            continue
        data[int(row['hour']), int(row['week']) - 1] = row['difference']

    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))

    maxv = np.ceil(max([np.max(data), 0 - np.min(data)])) + 0.2
    cs = ax.imshow(data, aspect='auto', interpolation='nearest',
                   vmin=(0 - maxv), vmax=maxv, cmap=plt.get_cmap(ctx['cmap']))
    a = fig.colorbar(cs)
    a.ax.set_ylabel(r"Temperature Departure $^{\circ}\mathrm{F}$")
    ax.grid(True)
    ab = ctx['_nt'].sts[station]['archive_begin']
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    ax.set_title(("[%s] %s %s-%s\nHourly Temp Departure "
                  "(skies were %s vs all)"
                  ) % (station, ctx['_nt'].sts[station]['name'],
                       max([ab.year, 1973]),
                       datetime.date.today().year, PDICT[ctx['which']]))
    ax.set_ylim(-0.5, 23.5)
    ax.set_ylabel("Local Hour of Day, %s" % (
        ctx['_nt'].sts[station]['tzname'],))
    ax.set_yticks((0, 4, 8, 12, 16, 20))
    ax.set_xticks(range(0, 55, 7))
    ax.set_xticklabels(('Jan 1', 'Feb 19', 'Apr 8', 'May 27', 'Jul 15',
                        'Sep 2', 'Oct 21', 'Dec 9'))

    ax.set_yticklabels(('Mid', '4 AM', '8 AM', 'Noon', '4 PM', '8 PM'))

    return fig, df


if __name__ == '__main__':
    plotter(dict())
