# -*- coding: utf-8 -*-
"""Time series plot.

    The coding line above needs to be first for python2.7.
"""
import datetime
from collections import OrderedDict

import pytz
import psycopg2.extras
import numpy as np
from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

MDICT = OrderedDict([
    ('tmpf', 'Air Temperature'),
    ('dwpf', 'Dew Point Temperature'),
    ('feel', 'Feels Like Temperature'),
    ('alti', 'Pressure Altimeter'),
    ('relh', 'Relative Humidity'),
    ('mslp', 'Sea Level Pressure')])
UNITS = {
    'tmpf': u'°F', 'dwpf': u'°F', 'alti': 'inch', 'mslp': 'mb',
    'feel': u'°F', 'relh': '%'}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    ts = datetime.date.today() - datetime.timedelta(days=365)
    desc['data'] = True
    desc['highcharts'] = True
    desc['description'] = """This chart displays a simple time series of
    an observed variable for a location of your choice.  For sites in the
    US, the daily high and low temperature climatology is presented as a
    filled bar for each day plotted when Air Temperature is selected."""
    desc['arguments'] = [
        dict(type='zstation', name='zstation', default='AMW',
             network='IA_ASOS', label='Select Station:'),
        dict(type='date', name='sdate', default=ts.strftime("%Y/%m/%d"),
             label='Start Date of Plot:',
             min="1951/01/01"),  # Comes back to python as yyyy-mm-dd
        dict(type='int', name='days', default='365',
             label='Days to Plot'),
        dict(type='select', name='var', options=MDICT, default='tmpf',
             label='Variable to Plot'),
    ]
    return desc


def highcharts(fdict):
    """ Highcharts output """
    ctx = get_data(fdict)
    ranges = []
    now = ctx['sdate']
    while ctx['climo'] is not None and now <= ctx['edate']:
        ranges.append([int(now.strftime("%s")) * 1000.,
                       ctx['climo'][now.strftime("%m%d")]['low'],
                       ctx['climo'][now.strftime("%m%d")]['high']])
        now += datetime.timedelta(days=1)

    j = dict()
    j['title'] = dict(text=('[%s] %s Time Series'
                            ) % (ctx['station'],
                                 ctx['_nt'].sts[ctx['station']]['name']))
    j['xAxis'] = dict(type='datetime')
    j['yAxis'] = dict(title=dict(text='%s %s' % (MDICT[ctx['var']],
                                                 UNITS[ctx['var']])))
    j['tooltip'] = {'crosshairs': True,
                    'shared': True,
                    'valueSuffix': " %s" % (UNITS[ctx['var']],)}
    j['legend'] = dict()
    j['global'] = {'useUTC': False}
    j['exporting'] = {'enabled': True}
    j['chart'] = {'zoomType': 'x'}
    j['plotOptions'] = {'line': {'turboThreshold': 0}}
    j['series'] = [
        {'name': MDICT[ctx['var']],
         'data': list(zip(ctx['df'].ticks.values.tolist(),
                          ctx['df'].datum.values.tolist())),
         'zIndex': 1,
         'color': '#FF0000',
         'lineWidth': 2,
         'marker': {'enabled': False},
         'type': 'line'}]
    if ranges:
        j['series'].append({
            'name': 'Range',
            'data': ranges,
            'type': 'arearange',
            'lineWidth': 0,
            'linkedTo': ':previous',
            'color': '#ADD8E6',
            'fillOpacity': 0.3,
            'zIndex': 0
         })

    return j


def get_data(fdict):
    """Get data common to both methods"""
    ctx = get_autoplot_context(fdict, get_description())
    asos_pgconn = get_dbconn('asos')
    coop_pgconn = get_dbconn('coop')
    ccursor = coop_pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx['station'] = ctx['zstation']
    sdate = ctx['sdate']
    days = ctx['days']
    ctx['edate'] = sdate + datetime.timedelta(days=days)
    today = datetime.date.today()
    if ctx['edate'] > today:
        ctx['edate'] = today
        ctx['days'] = (ctx['edate'] - sdate).days

    ctx['climo'] = None
    if ctx['var'] == 'tmpf':
        ctx['climo'] = {}
        ccursor.execute("""
            SELECT valid, high, low from ncdc_climate81 where station = %s
        """, (ctx['_nt'].sts[ctx['station']]['ncdc81'],))
        for row in ccursor:
            ctx['climo'][row[0].strftime("%m%d")] = dict(high=row[1],
                                                         low=row[2])
    if not ctx['climo']:
        raise NoDataFound("No data found.")
    col = "tmpf::int" if ctx['var'] == 'tmpf' else ctx['var']
    col = "dwpf::int" if ctx['var'] == 'dwpf' else col
    ctx['df'] = read_sql("""
        SELECT valid at time zone 'UTC' as valid,
        extract(epoch from valid) * 1000 as ticks,
        """ + col + """ as datum from alldata WHERE station = %s
        and valid > %s and valid < %s and """ + ctx['var'] + """ is not null
        and report_type = 2 ORDER by valid ASC
    """, asos_pgconn, params=(ctx['station'], sdate,
                              sdate + datetime.timedelta(days=days)),
                         index_col='valid')

    return ctx


def plotter(fdict):
    """ Go """
    ctx = get_data(fdict)

    (fig, ax) = plt.subplots(1, 1)

    xticks = []
    xticklabels = []
    now = ctx['sdate']
    cdates = []
    chighs = []
    clows = []
    while ctx['climo'] is not None and now <= ctx['edate']:
        cdates.append(now)
        chighs.append(ctx['climo'][now.strftime("%m%d")]['high'])
        clows.append(ctx['climo'][now.strftime("%m%d")]['low'])
        if now.day == 1 or (now.day % 12 == 0 and ctx['days'] < 180):
            xticks.append(now)
            fmt = "%-d"
            if now.day == 1:
                fmt = "%-d\n%b"
            xticklabels.append(now.strftime(fmt))

        now += datetime.timedelta(days=1)
    while now <= ctx['edate']:
        if now.day == 1 or (now.day % 12 == 0 and ctx['days'] < 180):
            xticks.append(now)
            fmt = "%-d"
            if now.day == 1:
                fmt = "%-d\n%b"
            xticklabels.append(now.strftime(fmt))
        now += datetime.timedelta(days=1)

    if chighs:
        chighs = np.array(chighs)
        clows = np.array(clows)
        ax.bar(cdates, chighs - clows, bottom=clows, fc='lightblue',
               ec='lightblue', label="Daily Climatology")
    # Construct a local timezone x axis
    x = ctx['df'].index.tz_localize(pytz.UTC).tz_convert(
        ctx['_nt'].sts[ctx['station']]['tzname']).tz_localize(None)
    ax.plot(x.values, ctx['df']['datum'], color='r',
            label='Hourly Obs')
    ax.set_ylabel("%s %s" % (MDICT[ctx['var']], UNITS[ctx['var']]))
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.set_xlim(ctx['sdate'], ctx['edate'])
    ax.set_ylim(top=ctx['df'].datum.max() + 15.)
    ax.legend(loc=2, ncol=2)
    ax.axhline(32, linestyle='-.')
    ax.grid(True)
    ax.set_title(("%s [%s]\n%s Timeseries %s - %s"
                  ) % (ctx['_nt'].sts[ctx['station']]['name'], ctx['station'],
                       MDICT[ctx['var']],
                       ctx['sdate'].strftime("%d %b %Y"),
                       ctx['edate'].strftime("%d %b %Y")))
    return fig, ctx['df']


if __name__ == '__main__':
    plotter(dict())
